
import os
import django
import sys
import re

# Set up Django environment
sys.path.append('/root/ALS_FTD_Research_Dashboard')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ALS_FTD_Research_Dashboard.settings')
django.setup()

from Dashboard.api_analytics import _get_active_trials_list, get_full_trials_dataset

print("--- DEBUGGING GENE NAMES ---")
full_data = get_full_trials_dataset()
print(f"Full Dataset Size: {len(full_data['trials'])}")

print("\n--- Inspecting first 20 genes from Full Dataset ---")
all_genes = set()
for t in full_data['trials']:
    if t.get('genes'):
        for g in t['genes']:
            all_genes.add(g)

sorted_genes = sorted(list(all_genes))
for g in sorted_genes[:20]:
    print(f"'{g}'")

print("\n--- Checking for 'Mutation' presence ---")
dirty = [g for g in sorted_genes if 'mutation' in g.lower()]
if dirty:
    print(f"FAILED: Found {len(dirty)} dirty genes: {dirty}")
else:
    print("SUCCESS: No genes with 'Mutation' found!")
