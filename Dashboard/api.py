from ninja import Router, schema
from typing import List
import re
import requests
from django.core.serializers.json import DjangoJSONEncoder
import json
from ninja.errors import ValidationError
from django.shortcuts import get_object_or_404
from .models import Trial, Gene, HealeyTrial
from .schemas import get_serialized_trials, GeneSchema, TrialSchema, ProcessedCriteriaSchema, HealeyTrialSchema, HealeyContactInfoSchema
from .utils import update_data, parse_criteria_from_response, extract_list_items, scrape_healey_platform_trial, send_criteria_to_ai_server
from .api_analytics import router as analytics_router
import os 
from django.conf import settings
from django.http import JsonResponse, HttpResponse
import csv
from io import StringIO
from typing import Any

router = Router()


@router.get("/", tags=["ClinicalTrials.gov API Fetch; Updated Nightly"])
def get_trials(request):
    update_data()  # Update the database records first
    trials = get_serialized_trials()
    return trials

@router.post("/AI-Eligibility-Descriptions", response=List[ProcessedCriteriaSchema], tags=["Testing Local AI's Classification of Eligibility Criteria"])
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

@router.get("/update-healey-trial", tags=["Update Healey Trial Web Scrape"])
def update_healey_trial(request):
    try:
        # Directly scrape and save the data
        scrape_healey_platform_trial()
        return JsonResponse({"message": "Healey trial data updated successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@router.get("/healey-trials", tags=["Download Healey Trials as JSON or CSV"])
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

@router.get("/genes", response=Any)
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