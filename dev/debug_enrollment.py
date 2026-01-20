import os
import django
from django.db.models import Count, Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ALS_FTD_Research_Dashboard.settings')
django.setup()

from Dashboard.models import Trial, Gene, Intervention

def debug_c9orf72():
    try:
        gene = Gene.objects.get(gene_symbol__iexact='C9orf72')
    except Gene.DoesNotExist:
        print("Gene C9orf72 not found")
        return

    print(f"Gene: {gene.gene_symbol}")
    
    # 1. Total Trials
    total_trials = gene.trials.all()
    print(f"Total Trials: {total_trials.count()}")
    
    # 2. Status Breakdown
    print("\nStatus Breakdown:")
    for t in total_trials:
        m2m_statuses = ", ".join([s.name for s in t.status.all()])
        print(f" - {t.unique_protocol_id}: {t.overall_status} -> [{m2m_statuses}]")

    # 3. Interventions
    drug_interventions = Intervention.objects.filter(
        trial__in=total_trials,
        intervention_type__icontains='Drug'
    )
    print(f"\nTotal Drug Interventions: {drug_interventions.count()}")
    
    # List some interventions if count is high
    if drug_interventions.count() > 0:
        print("Sample Interventions:")
        for i in drug_interventions[:10]:
            print(f" - {i.intervention_type}: {i.intervention_description[:50]}...")

    # 6. Check intervention_types JSON
    print("\nIntervention Types (JSON):")
    for t in total_trials:
        if t.intervention_types:
            print(f" - {t.unique_protocol_id}: {t.intervention_types}")

if __name__ == '__main__':
    debug_c9orf72()