import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ALS_FTD_Research_Dashboard.settings')
django.setup()

from Dashboard.api_analytics import get_full_trials_dataset, _get_active_trials_list

def debug_api_vcp():
    print("--- Testing API Serialization for VCP ---")
    
    # Get active trials as the Trial Finder would
    active_trials = _get_active_trials_list()
    
    vcp_trials = [t for t in active_trials if 'VCP' in [g.upper() for g in t.get('genes', [])]]
    
    print(f"Total Active Trials found by API: {len(active_trials)}")
    print(f"VCP Trials found by API: {len(vcp_trials)}")
    
    for t in vcp_trials:
        print(f"ID: {t['id']}")
        print(f"  Status: {t['status']}")
        print(f"  Genes: {t['genes']}")
        print("-" * 20)

    # Also check if 'VCP' is in filter options
    from Dashboard.api_analytics import get_filter_options
    options = get_filter_options(None)
    print(f"VCP in filter options? {'VCP' in options['genes']}")
    if not 'VCP' in options['genes']:
        print(f"Genes in options: {options['genes']}")

if __name__ == '__main__':
    debug_api_vcp()