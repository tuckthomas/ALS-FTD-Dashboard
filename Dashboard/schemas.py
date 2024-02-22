from .models import Gene, Trial
from pydantic import BaseModel, validator, ValidationError, Field, HttpUrl, json
from typing import List, Optional, Union
from datetime import datetime, date
from pydantic.networks import AnyHttpUrl
from django.forms.models import model_to_dict
import json

class GeneSchema(BaseModel):
    gene_symbol: str
    gene_name: str
    gene_risk_category: str

class TrialSchema(BaseModel):
    unique_protocol_id: str
    nct_id: Optional[str] = None
    brief_title: Optional[str] = None
    study_type: Optional[str] = None
    study_phase: Optional[str] = None
    overall_status: Optional[str] = None
    study_submitance_date: Optional[date] = None
    study_submitance_date_qc: Optional[date] = None
    study_start_date: Optional[date] = None
    study_start_date_type: Optional[str] = None
    status_verified_date: Optional[date] = None
    completion_date: Optional[date] = None
    lead_sponsor_name: Optional[str] = None
    responsible_party_type: Optional[str] = None
    responsible_party_investigator_full_name: Optional[str] = None
    condition: Optional[Union[str, List[str]]] = None
    keyword: Optional[Union[str, List[str]]] = None
    intervention_name: Optional[Union[str, List[dict]]] = None
    study_population: Optional[str] = None
    enrollment_count: Optional[int] = None
    enrollment_type: Optional[str] = None
    fda_regulated_drug: Optional[str] = None
    fda_regulated_device: Optional[str] = None
    primary_outcomes: Optional[Union[str, List[dict]]] = None
    secondary_outcomes: Optional[Union[str, List[dict]]] = None
    other_outcomes: Optional[Union[str, List[dict]]] = None
    clinical_trial_url: Optional[str] = None
    study_location: Optional[Union[str, List[dict]]] = None
    genes: Optional[List[str]] = None


    # Prepare URL for JSON serialization
    def dict(self, **kwargs):
        return super().dict(
            **kwargs,
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
        )

     # Custom serialization method for HttpUrl fields
    class Config:
        json_encoders = {
            AnyHttpUrl: lambda v: str(v),  # Convert AnyHttpUrl to str during serialization
        }

    @validator('study_submitance_date', 'study_submitance_date_qc', 'study_start_date', 'status_verified_date', 'completion_date', pre=True, always=True)
    def parse_date(cls, value):
        if value is None:
            return None
        if isinstance(value, date):
            # If it's already a date object, return it directly
            return value
        try:
            # Attempt to directly parse the date if in full `YYYY-MM-DD` format
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            try:
                # Handle `YYYY-MM` format by assuming the first day of the month
                return datetime.strptime(value, '%Y-%m').date()
            except ValueError:
                try:
                    # Handle `M-D-YYYY` format
                    return datetime.strptime(value, '%m-%d-%Y').date()
                except ValueError:
                    # Raise an error if none of the formats match
                    raise ValidationError(f"Date format for {value} is not supported.")

# Function to fetch and serialize trials from the database
def get_serialized_trials():
    serialized_trials = []
    for trial in Trial.objects.all():  # No need to prefetch_related('genes') since 'genes' is now a JSONField
        trial_dict = model_to_dict(trial, exclude=['id', 'genes']) 

        # Convert the JSON string fields to dictionaries, if needed
        for field in ['study_phase', 'condition', 'keyword', 'intervention_name', 'study_location', 'primary_outcomes', 'secondary_outcomes', 'other_outcomes']:
            field_value = getattr(trial, field, None)
            if isinstance(field_value, str):
                # If the field is a string, attempt to load it as JSON
                try:
                    trial_dict[field] = json.loads(field_value)
                except json.JSONDecodeError:
                    # If JSON decoding fails, leave the field as is
                    pass
            else:
                trial_dict[field] = field_value  # If it's already a dict, use it as is

        # No need to manually convert 'genes' as it should already be in the correct format
        trial_dict['genes'] = getattr(trial, 'genes', None)

        # Create a TrialSchema instance using the trial_dict
        trial_schema = TrialSchema(**trial_dict)
        # Append the serialized form of the TrialSchema instance to the list of serialized trials
        serialized_trials.append(trial_schema.dict())

    return serialized_trials
