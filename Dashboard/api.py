from ninja import Router, schema, Query
from typing import List, Optional
import re
import requests
from datetime import date
from django.core.serializers.json import DjangoJSONEncoder
import json
from ninja.errors import ValidationError
from django.shortcuts import get_object_or_404
from .models import Trial, Gene, HealeyTrial, ContactSubmission, IssueReport, NewsArticle
from .schemas import get_serialized_trials, GeneSchema, TrialSchema, ProcessedCriteriaSchema, HealeyTrialSchema, HealeyContactInfoSchema, ContactSubmissionSchema, IssueReportSchema, NewsArticleSchema
from .utils import update_data, parse_criteria_from_response, extract_list_items, scrape_healey_platform_trial, send_criteria_to_ai_server
from .api_analytics import router as analytics_router
import os 
from django.conf import settings
from django.http import JsonResponse, HttpResponse
import csv
from io import StringIO
from typing import Any

router = Router()
news_router = Router()
contact_router = Router()
genes_router = Router()
trials_router = Router()

@news_router.get("/", response=List[NewsArticleSchema], tags=["News Aggregator"])
def get_news(request, 
             genes: List[str] = Query(None), 
             start_date: date = None, 
             end_date: date = None,
             limit: int = 100):
    
    queryset = NewsArticle.objects.all()

    if genes:
        # Filter articles that are linked to ANY of the provided gene symbols
        queryset = queryset.filter(related_genes__gene_symbol__in=genes).distinct()

    if start_date:
        queryset = queryset.filter(publication_date__date__gte=start_date)
    
    if end_date:
        queryset = queryset.filter(publication_date__date__lte=end_date)

    return queryset.order_by('-publication_date')[:limit]

@contact_router.post("/", tags=["User Feedback"])
def submit_contact_form(request, data: ContactSubmissionSchema):
    try:
        ContactSubmission.objects.create(**data.dict())
        return {"success": True, "message": "Thank you for your message. We will be in touch shortly."}
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@contact_router.post("/report-issue", tags=["User Feedback"])
def report_issue(request, data: IssueReportSchema):
    try:
        IssueReport.objects.create(**data.dict())
        return {"success": True, "message": "Issue reported successfully. Thank you for your feedback."}
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@trials_router.get("/", tags=["ClinicalTrials.gov API Fetch; Updated Nightly"])
def get_trials(request):
    # update_data()  # REMOVED: Blocking call caused 504 timeouts. Use /sync-trials instead.
    trials = get_serialized_trials()
    return trials

@trials_router.post("/sync-trials", tags=["Trigger Data Scrape (Manual/Cron)"])
def sync_trials(request):
    try:
        update_data()
        return JsonResponse({"message": "Data synchronization complete."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@trials_router.post("/AI-Eligibility-Descriptions", response=List[ProcessedCriteriaSchema], tags=["Testing Local AI's Classification of Eligibility Criteria"])
def ai_eligibility_description(request):
    # This endpoint wraps the process_trials_with_ai logic for Ninja
    trials = Trial.objects.filter(eligibility_criteria_generic_description__isnull=False) #[:15]  # Adjust as necessary
    processed_trials = []

    for trial in trials:
        response = send_criteria_to_ai_server(trial.unique_protocol_id, trial.eligibility_criteria_generic_description)
        
        if response:
            trial.eligibility_criteria_inclusion_description = json.dumps(response.get('inclusion', []), cls=DjangoJSONEncoder)
            trial.eligibility_criteria_exclusion_description = json.dumps(response.get('exclusion', []), cls=DjangoJSONEncoder)
            trial.save()
            processed_trial = {
                "unique_protocol_id": trial.unique_protocol_id,
                "inclusion_criteria": response.get('inclusion', []),
                "exclusion_criteria": response.get('exclusion', [])
            }
            processed_trials.append(ProcessedCriteriaSchema(**processed_trial))

    return processed_trials

@trials_router.get("/update-healey-trial", tags=["Update Healey Trial Web Scrape"])
def update_healey_trial(request):
    try:
        # Directly scrape and save the data
        scrape_healey_platform_trial()
        return JsonResponse({"message": "Healey trial data updated successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@trials_router.get("/healey-trials", tags=["Download Healey Trials as JSON or CSV"])
def get_healey_trials(request, format: str = "json") -> Any:
    trials = HealeyTrial.objects.all()
    
    if format.lower() == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        header = ['facility', 'state', 'enrollment_status', 'trial_contact_info']
        writer.writerow(header)
        for trial in trials:
            trial_contact_info_str = json.dumps(trial.trial_contact_info)
            row = [
                trial.facility,
                trial.state,
                trial.enrollment_status,
                trial_contact_info_str,
            ]
            writer.writerow(row)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="healey_trials.csv"'
        return response
    elif format.lower() == 'json':
        trials_data = list(trials.values('facility', 'state', 'enrollment_status', 'trial_contact_info'))
        return JsonResponse(trials_data, safe=False)
    else:
        return JsonResponse({'error': 'Unsupported format specified. Please use either "json" or "csv".'}, status=400)

@genes_router.get("/", response=Any)
def get_genes(request, format: str = "json"):
    genes = Gene.objects.all().values_list('gene_symbol', 'gene_name', 'gene_risk_category')
    
    if format.lower() == "csv":
        # Create a buffer to hold CSV data
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['gene_symbol', 'gene_name', 'gene_risk_category'])
        writer.writerows(genes)

        # Set HTTP response headers for CSV file download
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="genes.csv"'
        return response

    # Default to JSON
    return list(genes)


@genes_router.get("/{symbol}", tags=["Gene Data"])
def get_gene_detail(request, symbol: str):
    """Get detailed information for a specific gene."""
    from .models import GeneStructure
    try:
        gene = Gene.objects.get(gene_symbol__iexact=symbol)
        structures = gene.structures.all()
        return {
            "gene_symbol": gene.gene_symbol,
            "gene_name": gene.gene_name,
            "gene_risk_category": gene.gene_risk_category,
            "structures": [
                {
                    "id": s.id,
                    "source_type": s.source_type,
                    "external_id": s.external_id,
                    "title": s.title,
                    "is_primary": s.is_primary,
                }
                for s in structures
            ]
        }
    except Gene.DoesNotExist:
        return JsonResponse({"error": f"Gene {symbol} not found"}, status=404)


@genes_router.get("/{symbol}/structure", tags=["Gene Data"])
def get_gene_structure(request, symbol: str):
    """Get the primary 3D structure for a gene."""
    from .models import GeneStructure
    try:
        gene = Gene.objects.get(gene_symbol__iexact=symbol)
        # Get primary structure, or first available
        structure = gene.structures.filter(is_primary=True).first()
        if not structure:
            structure = gene.structures.first()
        
        if not structure:
            return JsonResponse({"error": f"No structure available for {symbol}"}, status=404)
        
        return {
            "gene": {
                "symbol": gene.gene_symbol,
                "name": gene.gene_name,
            },
            "structure": {
                "id": structure.id,
                "source_type": structure.source_type,
                "external_id": structure.external_id,
                "title": structure.title,
                "componentProps": structure.get_component_props(),
            }
        }
    except Gene.DoesNotExist:
        return JsonResponse({"error": f"Gene {symbol} not found"}, status=404)