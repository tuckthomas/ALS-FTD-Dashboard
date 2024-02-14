from datetime import datetime
from pydantic import BaseModel, validator, ValidationError
from typing import List, Optional
from .models import Gene, Trial

class GeneSchema(BaseModel):
    gene_symbol: str
    gene_name: str
    gene_risk_category: str

class TrialSchema(BaseModel):
    unique_protocol_id: str
    brief_title: Optional[str]
    study_type: Optional[str]
    overall_status: Optional[str]
    status_verified_date: Optional[datetime]
    completion_date: Optional[datetime]
    lead_sponsor_name: Optional[str]
    responsible_party_type: Optional[str]
    responsible_party_investigator_full_name: Optional[str]
    condition: Optional[str]
    keyword: Optional[str]
    intervention_name: Optional[str]
    study_population: Optional[str]
    enrollment_count: Optional[int]
    enrollment_type: Optional[str]
    genes: Optional[List[GeneSchema]]

    @validator('status_verified_date', 'completion_date', pre=True, always=True)
    def parse_date(cls, value):
        if value is None:
            return None
        try:
            # Attempt to directly parse the date if in full `YYYY-MM-DD` format
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            try:
                # Handle `YYYY-MM` format by assuming the first day of the month
                return datetime.strptime(value, '%Y-%m')
            except ValueError:
                try:
                    # Handle `M-D-YYYY` format
                    return datetime.strptime(value, '%m-%d-%Y')
                except ValueError:
                    # Raise an error if none of the formats match
                    raise ValidationError(f"Date format for {value} is not supported.")

# Function to fetch and serialize trials from the database
def get_serialized_trials():
    serialized_trials = []
    for trial in Trial.objects.prefetch_related('genes').all():
        serialized_trials.append(
            TrialSchema(
                unique_protocol_id=trial.unique_protocol_id,
                brief_title=trial.brief_title,
                genes=[GeneSchema(
                    gene_symbol=gene.gene_symbol,
                    gene_name=gene.gene_name,
                    gene_risk_category=gene.gene_risk_category
                ) for gene in trial.genes.all()]
            )
        )
    return serialized_trials

