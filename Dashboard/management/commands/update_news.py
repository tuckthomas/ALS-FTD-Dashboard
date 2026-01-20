from django.core.management.base import BaseCommand
from Dashboard.news_scraper import fetch_and_process_news

class Command(BaseCommand):
    help = 'Fetches latest ALS/FTD news from RSS feeds'

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching news...")
        count = fetch_and_process_news()
        self.stdout.write(self.style.SUCCESS(f"Successfully added {count} new articles."))
