import feedparser
import re
from urllib.parse import quote
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import NewsArticle, Gene
import logging
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)

# List of RSS feeds to scrape
RSS_FEEDS = [
    # Specialized Medical Feeds
    "https://www.sciencedaily.com/rss/mind_brain/als.xml",
    "https://medicalxpress.com/rss/tags/amyotrophic+lateral+sclerosis/",
    "https://www.news-medical.net/tag/feed/Amyotrophic-Lateral-Sclerosis-ALS.aspx",
    "https://medicalxpress.com/rss/tags/frontotemporal+dementia/",
    
    # PubMed (Research Studies - High Volume)
    "https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=%28Amyotrophic+Lateral+Sclerosis%29+OR+%28Frontotemporal+Dementia%29+OR+%28Lou+Gehrig%27s+Disease%29&limit=50",

    # Google News RSS (Broad Coverage - Removed time limits for better backfill)
    "https://news.google.com/rss/search?q=Amyotrophic+Lateral+Sclerosis&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Frontotemporal+Dementia&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Lou+Gehrig%27s+Disease&hl=en-US&gl=US&ceid=US:en"
]

def normalize_title(title):
    """
    Normalizes a title by lowercasing, removing punctuation, 
    and stripping common source suffixes like " - Yahoo News" or " | Reuters".
    """
    if not title:
        return ""
    
    # Lowercase
    t = title.lower()
    
    # Remove common source suffixes (often added by aggregators like Google News)
    # Matches patterns like " - Source Name", " | Source Name", " : Source Name"
    t = re.split(r' \- | \| | \: ', t)[0]
    
    # Remove non-alphanumeric characters (including punctuation)
    t = re.sub(r'[^a-z0-9\s]', '', t)
    
    # Strip whitespace and collapse multiple spaces
    t = " ".join(t.split())
    
    return t

def is_fuzzy_duplicate(new_norm_title, existing_items, threshold=85):
    """
    Checks if new_norm_title is a fuzzy match for any title in existing_items.
    existing_items can be a list of normalized strings or a dictionary of such strings.
    """
    if not new_norm_title:
        return None
        
    for existing_title in existing_items:
        # token_set_ratio is robust against different word orders and extra words
        score = fuzz.token_set_ratio(new_norm_title, existing_title)
        if score >= threshold:
            return existing_title
    return None

def get_source_priority(feed_url, entry=None):
    """
    Returns a priority score for a feed/entry. Lower is better.
    1: Scientific Journals / PubMed
    2: Specialized Medical News (ScienceDaily, MedicalXpress)
    3: Major International News (Reuters, AP, BBC)
    4: Regional/Local News
    5: General Aggregators (Google News, Yahoo)
    """
    url = feed_url.lower()
    
    if 'pubmed' in url:
        return 1
    
    specialized = ['sciencedaily', 'medicalxpress', 'news-medical', 'alsnewstoday']
    if any(s in url for s in specialized):
        return 2
    
    if 'news.google.com' in url or 'yahoo' in url:
        return 5
        
    return 4

def fetch_and_process_news():
    """
    Fetches news from RSS feeds, filters by ALS/FTD and Gene keywords,
    and saves new articles to the database, prioritizing primary sources
    and applying fuzzy deduplication.
    """
    logger.info("Starting news scrape...")
    
    # 1. Build Keyword List from Database
    gene_objects = Gene.objects.exclude(gene_risk_category='Tenuous')
    base_keywords = {
        "ALS", "Amyotrophic Lateral Sclerosis", 
        "FTD", "Frontotemporal Dementia", 
        "Lou Gehrig's Disease", "Motor Neuron Disease"
    }
    
    keyword_to_gene = {}
    all_keywords = base_keywords.copy()
    dynamic_feeds = []

    for gene in gene_objects:
        if gene.gene_name:
            name = gene.gene_name.upper()
            keyword_to_gene[name] = gene
            all_keywords.add(name)
        
        if gene.gene_symbol:
            symbol = gene.gene_symbol.upper()
            keyword_to_gene[symbol] = gene
            all_keywords.add(symbol)
            
            # PubMed
            raw_pubmed_query = f"({symbol}) AND (ALS OR Amyotrophic Lateral Sclerosis OR FTD OR Frontotemporal Dementia)"
            encoded_pubmed_query = quote(raw_pubmed_query)
            dynamic_feeds.append(f"https://pubmed.ncbi.nlm.nih.gov/rss/search/?term={encoded_pubmed_query}&limit=5")
            
            # Google News
            raw_gnews_query = f"{symbol} ALS"
            encoded_gnews_query = quote(raw_gnews_query)
            dynamic_feeds.append(f"https://news.google.com/rss/search?q={encoded_gnews_query}&hl=en-US&gl=US&ceid=US:en")
        
    all_feeds = RSS_FEEDS + dynamic_feeds

    # 2. Buffer articles from this run to resolve duplicates across feeds
    article_buffer = {}
    
    # Load recent DB articles for cross-run duplicate prevention (last 7 days)
    recent_cutoff = make_aware(datetime.now() - timedelta(days=7))
    recent_articles = NewsArticle.objects.filter(publication_date__gte=recent_cutoff)
    db_recent_titles = {normalize_title(a.title) for a in recent_articles if a.title}

    for feed_url in all_feeds:
        try:
            feed = feedparser.parse(feed_url)
            priority = get_source_priority(feed_url)
            
            for entry in feed.entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                
                if NewsArticle.objects.filter(url=link).exists():
                    continue
                
                norm_title = normalize_title(title)
                if not norm_title:
                    continue

                # Fuzzy Check against DB
                if is_fuzzy_duplicate(norm_title, db_recent_titles):
                    continue
                
                # Fuzzy Check against Buffer
                match_in_buffer = is_fuzzy_duplicate(norm_title, article_buffer.keys())
                
                if match_in_buffer:
                    existing_key = match_in_buffer
                    existing = article_buffer[existing_key]
                    
                    published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                    pub_date = make_aware(datetime(*published_parsed[:6])) if published_parsed else make_aware(datetime(2000, 1, 1))

                    time_diff_seconds = (existing['data']['publication_date'] - pub_date).total_seconds()
                    
                    replace = False
                    if time_diff_seconds > 14400: # New one is > 4 hours older
                        replace = True
                    elif time_diff_seconds < -14400: # Existing one is > 4 hours older
                        replace = False
                    else:
                        if priority < existing['priority']:
                            replace = True
                        elif priority > existing['priority']:
                            replace = False
                        else:
                            replace = pub_date < existing['data']['publication_date']
                    
                    if not replace:
                        continue
                    else:
                        if existing_key != norm_title:
                            del article_buffer[existing_key]
                
                # Process and Buffer
                summary = entry.get('summary', '') or entry.get('description', '')
                full_text = (title + " " + summary).upper()
                
                matched_keywords = []
                for keyword in all_keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', full_text):
                        matched_keywords.append(keyword)
                
                if matched_keywords:
                    published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                    pub_date = make_aware(datetime(*published_parsed[:6])) if published_parsed else make_aware(datetime(2000, 1, 1))

                    article_buffer[norm_title] = {
                        'priority': priority,
                        'feed_title': feed.feed.get('title', 'Unknown Source'),
                        'data': {
                            'title': title,
                            'summary': summary,
                            'url': link,
                            'publication_date': pub_date,
                            'matched_keywords': matched_keywords,
                            'image_url': None
                        }
                    }
                    
                    if 'media_content' in entry:
                        article_buffer[norm_title]['data']['image_url'] = entry.media_content[0]['url']
                    elif 'links' in entry:
                        for l in entry.links:
                            if l.get('type', '').startswith('image/'):
                                article_buffer[norm_title]['data']['image_url'] = l['href']
                                break
        except Exception as e:
            logger.error(f"Failed to process feed {feed_url}: {e}")

    # 3. Save to DB
    new_articles_count = 0
    for norm_title, item in article_buffer.items():
        data = item['data']
        try:
            article = NewsArticle.objects.create(
                title=data['title'],
                summary=data['summary'],
                content=data['summary'],
                source_name=item['feed_title'],
                url=data['url'],
                image_url=data['image_url'],
                publication_date=data['publication_date'],
                tags=data['matched_keywords'][:5]
            )
            related_genes = [keyword_to_gene[k] for k in data['matched_keywords'] if k in keyword_to_gene]
            if related_genes:
                article.related_genes.set(related_genes)
            new_articles_count += 1
        except Exception as e:
            logger.error(f"Error saving article {data['title']}: {e}")

    logger.info(f"News scrape complete. Added {new_articles_count} new articles.")
    return new_articles_count