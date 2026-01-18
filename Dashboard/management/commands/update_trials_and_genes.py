from django.core.management.base import BaseCommand
# Import your function here
from Dashboard.utils import update_data

class Command(BaseCommand):
    help = 'Updates the trials and genes data in the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting the update process...'))
        update_data()
        self.stdout.write(self.style.SUCCESS('Update process completed successfully.'))
