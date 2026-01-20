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

class InterventionSchema(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None

class TrialSchema(BaseModel):
    unique_protocol_id: str
    nct_id: Optional[str] = None
    brief_title: Optional[str] = None
    brief_description: Optional[str] = None
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
    intervention: Optional[Union[str, List[dict]]] = None
    intervention_name: Optional[List[InterventionSchema]] = None
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
    eligibility_criteria_generic_description: Optional[str] = None
    eligibility_criteria_inclusion_description: Optional[List[str]] = None
    eligibility_criteria_exclusion_description: Optional[List[str]] = None
    eligibility_criteria_healthy_volunteers: Optional[str] = None
    eligibility_criteria_sex: Optional[str] = None
    eligibility_criteria_min_age_years: Optional[str] = None
    eligibility_criteria_max_age_years: Optional[str] = None


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

    @validator('intervention_name', pre=True)
    def validate_intervention_name(cls, value):
        if value == '' or value is None:
            return []  # Treat as an empty list if an empty string or None
        if not isinstance(value, list):
            raise ValueError('intervention_name must be a list')
        for idx, item in enumerate(value):
            if not isinstance(item, dict):
                # Convert non-dict items into a dictionary with a default description
                item = {'type': item, 'description': 'No description provided'}
            else:
                # Ensure each dictionary has a 'type' and 'description'
                if 'type' not in item:
                    item['type'] = 'Not specified'
                if 'description' not in item:
                    item['description'] = 'No description provided'
            value[idx] = item
        return value

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
        for field in ['study_phase', 'condition', 'keyword', 'intervention_types', 'intervention_name', 'study_location', 'primary_outcomes', 'secondary_outcomes', 'other_outcomes', 'eligibility_criteria_inclusion_description', 'eligibility_criteria_exclusion_description']:
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

class CriteriaSchema(BaseModel):
    inclusion_criteria: Optional[List[str]]
    exclusion_criteria: Optional[List[str]]

class ProcessedCriteriaSchema(BaseModel):
    unique_protocol_id: str
    inclusion_criteria: List[str] = []
    exclusion_criteria: List[str] = []

    @validator('inclusion_criteria', 'exclusion_criteria', pre=True)
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Input should be a valid JSON list')
        return v

class HealeyContactInfoSchema(BaseModel):
    trial_contact_name: Optional[str] = Field(default="")
    trial_contact_email: Optional[str] = Field(default="")
    trial_contact_phone_numer: Optional[str] = Field(default="")

class HealeyTrialSchema(BaseModel):
    facility: str
    state: Optional[str] = None
    enrollment_status: Optional[str] = None
    trial_contact_info: List[HealeyContactInfoSchema]

class ContactSubmissionSchema(BaseModel):
    name: str
    email: str
    subject: str
    message: str

class IssueReportSchema(BaseModel):
    title: str
    description: str
    steps_to_reproduce: Optional[str] = None
    browser_info: Optional[str] = None
    reported_by: Optional[str] = None # Email address

class NewsArticleSchema(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    source_name: str
    url: str
    image_url: Optional[str] = None
    publication_date: datetime
    tags: List[str] = []

    class Config:
        from_attributes = True