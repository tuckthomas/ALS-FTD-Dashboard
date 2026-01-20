import os
import django
from django.db.models import Count, Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ALS_FTD_Research_Dashboard.settings')
django.setup()

from Dashboard.models import Trial, Gene, Intervention

def debug_sod1():
    try:
        gene = Gene.objects.get(gene_symbol__iexact='SOD1')
    except Gene.DoesNotExist:
        print("Gene SOD1 not found")
        return

    print(f"Gene: {gene.gene_symbol}")
    
    # Active definition
    active_statuses = ['RECRUITING', 'ENROLLING_BY_INVITATION', 'NOT_YET_RECRUITING', 'AVAILABLE']
    
    active_trials = gene.trials.filter(overall_status__in=active_statuses)
    print(f"Active Trials (Actionable): {active_trials.count()}")
    
    for t in active_trials:
        interventions = t.interventions.all()
        drug_interventions = interventions.filter(intervention_type__icontains='Drug')
        print(f" - {t.unique_protocol_id} ({t.overall_status}): {interventions.count()} total interventions, {drug_interventions.count()} drugs")
        for i in interventions:
             print(f"    * [{i.intervention_type}] {i.intervention_name}: {i.intervention_description[:50]}")

if __name__ == '__main__':
    debug_sod1()
