
import os
import django
import sys

sys.path.append('/root/ALS_FTD_Research_Dashboard')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ALS_FTD_Research_Dashboard.settings")
django.setup()

from Dashboard.models import Gene

def get_categories():
    categories = Gene.objects.values_list('gene_risk_category', flat=True).distinct().order_by('gene_risk_category')
    print("Unique Gene Risk Categories:")
    print("-" * 30)
    for cat in categories:
        print(f"- {cat}")

if __name__ == '__main__':
    get_categories()
