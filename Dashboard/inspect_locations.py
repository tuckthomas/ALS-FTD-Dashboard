
import os
import django
import sys
import json

# Setup Django environment
sys.path.append('/root/ALS_FTD_Research_Dashboard')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ALS_FTD_Research_Dashboard.settings')
django.setup()

from Dashboard.models import Trial

# Get first 5 trials with study_location
trials = Trial.objects.exclude(study_location__isnull=True).exclude(study_location={})[:5]

print("--- Study Location Samples ---")
for trial in trials:
    print(f"Trial: {trial.nct_id}")
    print(json.dumps(trial.study_location, indent=2))
    print("-" * 20)
