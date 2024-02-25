from ninja import Router, schema
from typing import List
import re
from django.core.serializers.json import DjangoJSONEncoder
import json
from ninja.errors import ValidationError
from django.shortcuts import get_object_or_404
from .models import Trial, Gene
from .schemas import get_serialized_trials, GeneSchema, TrialSchema, ProcessedCriteriaSchema
from .utils import update_data, parse_criteria_from_response, extract_list_items, send_criteria_to_ai_server
import pandas as pd
import os 
from django.conf import settings

router = Router()

@router.get("/", tags=["Trials"])
def get_trials(request):
    update_data()  # Update the database records first
    trials = get_serialized_trials()
    return trials

@router.post("/AI-Eligibility-Descriptions", response=List[ProcessedCriteriaSchema], tags=["Trials"])
def ai_eligibility_description(request):
    # This endpoint wraps the process_trials_with_ai logic for Ninja
    trials = Trial.objects.filter(eligibility_criteria_generic_description__isnull=False)[:15]  # Adjust as necessary
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
