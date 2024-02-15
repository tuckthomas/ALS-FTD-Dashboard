from .models import Gene, Trial
from pydantic import BaseModel, validator, ValidationError, Field, HttpUrl
from typing import List, Optional, Union
from datetime import datetime, date
from pydantic.networks import AnyHttpUrl
from django.forms.models import model_to_dict

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
    study_submitance_date: Optional[datetime] = None
    study_submitance_date_qc: Optional[datetime] = None
    study_start_date: Optional[datetime] = None
    study_start_date_type: Optional[str] = None
    status_verified_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    lead_sponsor_name: Optional[str] = None
    responsible_party_type: Optional[str] = None
    responsible_party_investigator_full_name: Optional[str] = None
    condition: Optional[str] = None
    keyword: Optional[str] = None
    intervention_name: Optional[str] = None
    study_population: Optional[str] = None
    enrollment_count: Optional[int] = None
    enrollment_type: Optional[str] = None
    expanded_access: Optional[str] = None
    fda_regulated_drug: Optional[str] = None
    fda_regulated_device: Optional[str] = None
    clinical_trial_url: Optional[str] = None
    genes: Optional[List[GeneSchema]] = Field(default_factory=list)

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
    for trial in Trial.objects.prefetch_related('genes').all():
        # Ensure URL is a string
        clinical_trial_url = str(trial.clinical_trial_url) if trial.clinical_trial_url else None
        trial_data = TrialSchema(
            unique_protocol_id=trial.unique_protocol_id,
            nct_id=trial.nct_id,
                brief_title=trial.brief_title,
                study_type=trial.study_type,
                study_phase=trial.study_phase,
                overall_status=trial.overall_status,
                study_submitance_date=trial.study_submitance_date,
                study_submitance_date_qc=trial.study_submitance_date_qc,
                study_start_date=trial.study_start_date,
                study_start_date_type=trial.study_start_date_type,
                status_verified_date=trial.status_verified_date,
                completion_date=trial.completion_date,
                lead_sponsor_name=trial.lead_sponsor_name,
                responsible_party_type=trial.responsible_party_type,
                responsible_party_investigator_full_name=trial.responsible_party_investigator_full_name,
                condition=trial.condition,
                collaborators=trial.collaborators,
                keyword=trial.keyword,
                intervention_name=trial.intervention_name,
                study_population=trial.study_population,
                enrollment_count=trial.enrollment_count,
                enrollment_type=trial.enrollment_type,
                expanded_access=trial.expanded_access,
                fda_regulated_drug=trial.fda_regulated_drug,
                fda_regulated_device=trial.fda_regulated_device,
                clinical_trial_url=clinical_trial_url,
                genes=[GeneSchema(
                    gene_symbol=gene.gene_symbol,
                    gene_name=gene.gene_name,
                    gene_risk_category=gene.gene_risk_category
                ) for gene in trial.genes.all()]
            ).dict()
            
        serialized_trials.append(trial_data)

    return serialized_trials
