from django.core.management.base import BaseCommand
# Import your function here
from Dashboard.utils import update_data

class Command(BaseCommand):
    help = 'Updates the trials and genes data in the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting the update process...'))
        update_data()
        self.stdout.write(self.style.SUCCESS('Data update complete. Refreshing cache...'))
        
        # Refresh the API cache
        from django.core.cache import cache
        from Dashboard.api_analytics import get_full_trials_dataset, get_dashboard_package
        
        # 1. Refresh Full Trials List
        get_full_trials_dataset()
        
        # 2. Refresh Dashboard Packages (All & Familial)
        # Clear existing keys to force regeneration
        cache.delete('dashboard_package_familial_False')
        cache.delete('dashboard_package_familial_True')
        
        # Pre-warm the cache
        get_dashboard_package(request=None, familial=False)
        get_dashboard_package(request=None, familial=True)
        
        self.stdout.write(self.style.SUCCESS('Cache refreshed successfully. Update process complete.'))
