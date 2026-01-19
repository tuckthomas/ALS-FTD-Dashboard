
import os
import django
import sys
import json

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ALS_FTD_Research_Dashboard.settings')
django.setup()

from Dashboard.models import Trial, Gene

def backfill_genes():
    print("Starting backfill of related_genes...")
    trials = Trial.objects.all()
    count = 0
    updated_count = 0
    
    for trial in trials:
        count += 1
        raw_genes = trial.genes
        
        if not raw_genes:
            continue
            
        # Parse genes if it's a string, or use as is if it's a list
        gene_list = []
        if isinstance(raw_genes, str):
            try:
                # Handle potential JSON string or simple string
                # Ideally genes is a JSON field so Django gives us a python object (list)
                # But sometimes it might be saved as a string representation
                if raw_genes.startswith('['):
                    gene_list = json.loads(raw_genes)
                else:
                    gene_list = [raw_genes]
            except Exception as e:
                print(f"Error parsing genes for {trial.unique_protocol_id}: {raw_genes} - {e}")
                continue
        elif isinstance(raw_genes, list):
            gene_list = raw_genes
        else:
            print(f"Unknown type for genes in {trial.unique_protocol_id}: {type(raw_genes)}")
            continue

        # Now link existing genes
        # We assume genes in the list are gene symbols (strings)
        cleaned_list = []
        for g in gene_list:
            if isinstance(g, str):
                cleaned_list.append(g.strip())
            elif isinstance(g, dict) and 'gene_symbol' in g:
                 cleaned_list.append(g['gene_symbol'])
            # Add more parsing logic if necessary

        if not cleaned_list:
            continue

        genes_to_add = []
        for symbol in cleaned_list:
            # Case insensitive match? standardizing on uppercase usually best for symbols
            # But let's try exact match first as per current DB state
            gene_obj = Gene.objects.filter(gene_symbol__iexact=symbol).first()
            if gene_obj:
                genes_to_add.append(gene_obj)
            else:
                # print(f"Warning: Gene with symbol '{symbol}' not found in Gene table.")
                pass
        
        if genes_to_add:
            trial.related_genes.add(*genes_to_add)
            updated_count += 1
            print(f"Updated {trial.unique_protocol_id}: Added {len(genes_to_add)} genes.")

    print(f"Backfill complete. Processed {count} trials. Updated {updated_count} trials.")

if __name__ == "__main__":
    backfill_genes()
