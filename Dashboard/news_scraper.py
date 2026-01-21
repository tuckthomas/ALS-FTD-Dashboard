import feedparser
import re
from urllib.parse import quote
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import NewsArticle, Gene
import logging

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

def fetch_and_process_news():
    """
    Fetches news from RSS feeds, filters by ALS/FTD and Gene keywords,
    and saves new articles to the database.
    """
    logger.info("Starting news scrape...")
    
    # 1. Build Keyword List from Database
    # Filter out 'Tenuous' risk genes
    gene_objects = Gene.objects.exclude(gene_risk_category='Tenuous')
    
    # Base keywords (Using full names and abbreviations with safety)
    base_keywords = {
        "ALS", "Amyotrophic Lateral Sclerosis", 
        "FTD", "Frontotemporal Dementia", 
        "Lou Gehrig's Disease", "Motor Neuron Disease"
    }
    
    # Map keywords to Gene objects for linking
    keyword_to_gene = {}
    all_keywords = base_keywords.copy()
    
    # Dynamic Feed Generation
    dynamic_feeds = []

    for gene in gene_objects:
        # Use full gene name if available
        if gene.gene_name:
            name = gene.gene_name.upper()
            keyword_to_gene[name] = gene
            all_keywords.add(name)
        
        # Keep symbols as well, as they are standard identifiers (e.g. SOD1)
        if gene.gene_symbol:
            symbol = gene.gene_symbol.upper()
            keyword_to_gene[symbol] = gene
            all_keywords.add(symbol)
            
            # Generate PubMed Feed for this Gene + ALS/FTD context
            # Query: (Gene) AND (ALS OR Amyotrophic Lateral Sclerosis OR FTD OR Frontotemporal Dementia)
            raw_pubmed_query = f"({symbol}) AND (ALS OR Amyotrophic Lateral Sclerosis OR FTD OR Frontotemporal Dementia)"
            encoded_pubmed_query = quote(raw_pubmed_query)
            pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/rss/search/?term={encoded_pubmed_query}&limit=5"
            dynamic_feeds.append(pubmed_url)
            
            # Generate Google News Feed for this Gene
            # Query: Gene + "ALS"
            raw_gnews_query = f"{symbol} ALS"
            encoded_gnews_query = quote(raw_gnews_query)
            gnews_url = f"https://news.google.com/rss/search?q={encoded_gnews_query}&hl=en-US&gl=US&ceid=US:en"
            dynamic_feeds.append(gnews_url)
        
    logger.info(f"Loaded {len(all_keywords)} keywords for filtering.")
    logger.info(f"Generated {len(dynamic_feeds)} gene-specific RSS feeds.")

    new_articles_count = 0
    
    # Combine static and dynamic feeds
    all_feeds = RSS_FEEDS + dynamic_feeds

    for feed_url in all_feeds:
        try:
            feed = feedparser.parse(feed_url)
            logger.info(f"Parsing feed: {feed_url} ({len(feed.entries)} entries)")
            
            for entry in feed.entries:
                # 2. Check for relevance
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                link = entry.get('link', '')
                
                # Skip if already exists
                if NewsArticle.objects.filter(url=link).exists():
                    continue

                # Combine text for searching
                full_text = (title + " " + summary).upper()
                
                # Check if ANY keyword is present in the text using Regex Word Boundaries
                # This safely matches "ALS" but not "ALSO"
                matched_keywords = []
                for keyword in all_keywords:
                    # Escape keyword for regex safety (though mostly alphanumeric)
                    escaped_kw = re.escape(keyword)
                    # Use \b for word boundaries
                    if re.search(r'\b' + escaped_kw + r'\b', full_text):
                        matched_keywords.append(keyword)
                
                if matched_keywords:
                    # Identify related genes
                    related_genes = []
                    for k in matched_keywords:
                        if k in keyword_to_gene:
                            related_genes.append(keyword_to_gene[k])

                    # 3. Parse Date
                    published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                    if published_parsed:
                        pub_date = datetime(*published_parsed[:6])
                        pub_date = make_aware(pub_date)
                    else:
                        # Fallback to an old date instead of NOW to prevent it from showing as "Latest"
                        # Defaulting to Jan 1, 2000
                        pub_date = make_aware(datetime(2000, 1, 1))
                        # Only log warning if it's not a common occurrence to avoid log spam
                        # logger.warning(f"Could not parse date for article '{title}'. Defaulting to 2000-01-01.")

                    # 4. Extract Image (if available in media_content or summary)
                    image_url = None
                    if 'media_content' in entry:
                        image_url = entry.media_content[0]['url']
                    elif 'links' in entry:
                        for l in entry.links:
                            if l.get('type', '').startswith('image/'):
                                image_url = l['href']
                                break
                    
                    # 5. Save Article
                    article = NewsArticle.objects.create(
                        title=title,
                        summary=summary,
                        content=summary, # RSS usually only gives summary
                        source_name=feed.feed.get('title', 'Unknown Source'),
                        url=link,
                        image_url=image_url,
                        publication_date=pub_date,
                        tags=matched_keywords[:5] # Store top 5 matching keywords as tags
                    )
                    
                    # Link genes
                    if related_genes:
                        article.related_genes.set(related_genes)

                    new_articles_count += 1
                    
        except Exception as e:
            logger.error(f"Failed to process feed {feed_url}: {e}")

    logger.info(f"News scrape complete. Added {new_articles_count} new articles.")
    return new_articles_count