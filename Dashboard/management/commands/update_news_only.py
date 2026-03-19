from django.core.management.base import BaseCommand
from django.core.cache import cache
from Dashboard.news_scraper import fetch_and_process_news
from Dashboard.api_analytics import get_dashboard_package


class Command(BaseCommand):
    help = 'Fetches latest ALS/FTD news and refreshes the dashboard cache (lightweight, no trial sync)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching news...")
        count = fetch_and_process_news()
        self.stdout.write(self.style.SUCCESS(f"Successfully added {count} new articles."))

        # Clear dashboard cache so news_data is refreshed
        self.stdout.write("Refreshing dashboard cache...")
        cache.delete('dashboard_package_familial_v2_False')
        cache.delete('dashboard_package_familial_v2_True')

        # Pre-warm the cache
        get_dashboard_package(request=None, familial=False)
        get_dashboard_package(request=None, familial=True)

        self.stdout.write(self.style.SUCCESS("Cache refreshed. News update complete."))
