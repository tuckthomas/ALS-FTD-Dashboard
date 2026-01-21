from django.test import TestCase
from unittest.mock import patch, MagicMock
from .models import NewsArticle, Gene
from .news_scraper import fetch_and_process_news
from datetime import datetime
from django.utils.timezone import make_aware

class NewsScraperTest(TestCase):

    def setUp(self):
        # Create a test gene
        self.gene = Gene.objects.create(
            gene_symbol="SOD1",
            gene_name="Superoxide Dismutase 1",
            gene_risk_category="Definitive ALS gene"
        )

    @patch('Dashboard.news_scraper.feedparser.parse')
    def test_fetch_and_process_news_google_rss(self, mock_parse):
        # Mock Google News RSS entry
        mock_entry = MagicMock()
        mock_entry.get.side_effect = lambda k, d=None: {
            'title': 'New Study on Superoxide Dismutase 1 in Amyotrophic Lateral Sclerosis',
            'summary': 'Researchers discuss the impact of SOD1 mutations.',
            'link': 'https://news.google.com/articles/CAIiE...',
            'published_parsed': (2024, 1, 21, 12, 0, 0, 0, 0, 0)
        }.get(k, d)
        # Google News puts source in 'source' dict usually, but feedparser flattens it or puts it in feed.
        # Our scraper uses feed.feed.get('title') for source.
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feed.feed.get.return_value = "Google News - ALS"
        
        mock_parse.return_value = mock_feed

        # Run the scraper
        count = fetch_and_process_news()

        # Assertions
        self.assertEqual(count, 1)
        
        # Verify Article Data Schema
        article = NewsArticle.objects.get(url='https://news.google.com/articles/CAIiE...')
        self.assertEqual(article.title, 'New Study on Superoxide Dismutase 1 in Amyotrophic Lateral Sclerosis')
        self.assertEqual(article.source_name, 'Google News - ALS')
        self.assertIsNotNone(article.publication_date)
        
        # Verify Filtering & Linking
        # Should match "Amyotrophic Lateral Sclerosis" (base keyword) AND "Superoxide Dismutase 1" (gene name)
        # It should NOT match "ALS" if we removed it, but title has full name so it passes.
        
        self.assertTrue(article.related_genes.filter(gene_symbol='SOD1').exists())
        
        # Verify it captured the keywords in tags
        # matched keywords might include "SUPEROXIDE DISMUTASE 1", "AMYOTROPHIC LATERAL SCLEROSIS", "SOD1"
        print(f"Tags: {article.tags}")
        self.assertTrue(any("SUPEROXIDE DISMUTASE 1" in tag for tag in article.tags))

    @patch('Dashboard.news_scraper.feedparser.parse')
    def test_fetch_ignores_irrelevant(self, mock_parse):
        # Mock entry with NO keywords
        mock_entry = MagicMock()
        mock_entry.get.side_effect = lambda k, d=None: {
            'title': 'General Health Tips',
            'summary': 'Eat apples and stay healthy.',
            'link': 'http://example.com/health',
        }.get(k, d)
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feed.feed.get.return_value = "Random News"
        
        mock_parse.return_value = mock_feed

        count = fetch_and_process_news()
        
        self.assertEqual(count, 0)
        self.assertFalse(NewsArticle.objects.filter(url='http://example.com/health').exists())