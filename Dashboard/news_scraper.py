import feedparser
from datetime import datetime
from django.utils.timezone import make_aware
from .models import NewsArticle, Gene
import logging

logger = logging.getLogger(__name__)

# List of RSS feeds to scrape
RSS_FEEDS = [
    "https://www.sciencedaily.com/rss/mind_brain/als.xml",
    "https://medicalxpress.com/rss/tags/amyotrophic+lateral+sclerosis/",
    "https://www.news-medical.net/tag/feed/Amyotrophic-Lateral-Sclerosis-ALS.aspx",
    "https://www.sciencedaily.com/rss/mind_brain/dementia.xml", # For FTD coverage
    "https://medicalxpress.com/rss/tags/frontotemporal+dementia/"
]

def fetch_and_process_news():
    """
    Fetches news from RSS feeds, filters by ALS/FTD and Gene keywords,
    and saves new articles to the database.
    """
    logger.info("Starting news scrape...")
    
    # 1. Build Keyword List from Database
    # Filter out 'Tenuous' risk genes
    genes = Gene.objects.exclude(gene_risk_category='Tenuous').values_list('gene_symbol', 'gene_name')
    
    # Base keywords
    keywords = {
        "ALS", "Amyotrophic Lateral Sclerosis", 
        "FTD", "Frontotemporal Dementia", 
        "Lou Gehrig's Disease", "Motor Neuron Disease"
    }
    
    # Add High-Confidence Genes
    for symbol, name in genes:
        if symbol: keywords.add(symbol.upper())
        if name: keywords.add(name.upper())
        
    logger.info(f"Loaded {len(keywords)} keywords for filtering.")

    new_articles_count = 0

    for feed_url in RSS_FEEDS:
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
                
                # Check if ANY keyword is present in the text
                # We use word boundary check logic roughly by checking spaces, 
                # but simple substring match is usually fine for these specific scientific terms.
                matched_keywords = [k for k in keywords if k in full_text]
                
                if matched_keywords:
                    # 3. Parse Date
                    published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                    if published_parsed:
                        pub_date = datetime(*published_parsed[:6])
                        pub_date = make_aware(pub_date)
                    else:
                        pub_date = make_aware(datetime.now())

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
                    NewsArticle.objects.create(
                        title=title,
                        summary=summary,
                        content=summary, # RSS usually only gives summary
                        source_name=feed.feed.get('title', 'Unknown Source'),
                        url=link,
                        image_url=image_url,
                        publication_date=pub_date,
                        tags=matched_keywords[:5] # Store top 5 matching keywords as tags
                    )
                    new_articles_count += 1
                    
        except Exception as e:
            logger.error(f"Failed to process feed {feed_url}: {e}")

    logger.info(f"News scrape complete. Added {new_articles_count} new articles.")
    return new_articles_count
