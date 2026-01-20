
import os
import django
import sys

sys.path.append('/root/ALS_FTD_Research_Dashboard')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ALS_FTD_Research_Dashboard.settings")
django.setup()

from Dashboard.models import Trial

def list_statuses():
    statuses = Trial.objects.values_list('overall_status', flat=True).distinct().order_by('overall_status')
    print("Distinct Overall Statuses in DB:")
    print("-" * 30)
    for s in statuses:
        print(f"'{s}'")

if __name__ == '__main__':
    list_statuses()
