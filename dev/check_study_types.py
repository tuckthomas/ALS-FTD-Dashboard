import os
import django
from django.db.models import Count

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ALS_FTD_Research_Dashboard.settings")
django.setup()

from Dashboard.models import Trial

def check_study_types():
    print("Unique Study Types:")
    types = Trial.objects.values('study_type').annotate(count=Count('unique_protocol_id')).order_by('-count')
    for t in types:
        print(f"{t['study_type']}: {t['count']}")

if __name__ == "__main__":
    check_study_types()
