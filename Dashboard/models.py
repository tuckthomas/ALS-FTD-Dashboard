from django.db import models

# Table Update Log Update
class Update_Log(models.Model):
    database_table_name = models.CharField(max_length=255, primary_key=True)
    table_update_date = models.DateTimeField(null=True, blank=True) 

# Model for Gene List Information
class Gene(models.Model):
    gene_symbol = models.CharField(max_length=255)
    gene_name = models.CharField(max_length=255)
    gene_risk_category = models.CharField(max_length=255)

    def __str__(self):
        return self.gene_symbol

# Model for ClinicalTrials.gov Data
class Trial(models.Model):
    FDA_REGULATED_DRUG_CHOICES = [
        ('TRUE', 'True'),
        ('FALSE', 'False'),
        ('', '')
    ]

    FDA_REGULATED_DEVICE_CHOICES = [
        ('TRUE', 'True'),
        ('FALSE', 'False'),
        ('', '')
    ]

    ELIGIBILITY_CRITERIA_HEALTHY_VOLUNTEERS_CHOICES = [
        ('TRUE', 'True'),
        ('FALSE', 'False'),
        ('', '')
    ]

    unique_protocol_id = models.CharField(max_length=255, primary_key=True)  # Primary Key
    nct_id = models.CharField(max_length=255)
    brief_title = models.TextField(null=True, blank=True)
    study_type = models.CharField(max_length=255, null=True, blank=True)
    study_phase = models.CharField(max_length=50, null=True, blank=True)
    overall_status = models.CharField(max_length=255, null=True, blank=True)
    study_submitance_date = models.DateField(null=True, blank=True)
    study_submitance_date_qc = models.DateField(null=True, blank=True)
    study_start_date = models.DateField(null=True, blank=True)
    study_start_date_type = models.CharField(max_length=255, null=True, blank=True)
    status_verified_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    lead_sponsor_name = models.CharField(null=True, max_length=255, blank=True)
    responsible_party_type = models.CharField(null=True, max_length=255)
    responsible_party_investigator_full_name = models.CharField(null=True, max_length=255, blank=True)
    condition = models.JSONField(null=True, blank=True)
    collaborators = models.TextField(null=True, blank=True)
    keyword = models.JSONField(null=True, blank=True)
    intervention_types = models.JSONField(null=True, blank=True)
    intervention_name = models.JSONField(null=True, blank=True)
    study_population = models.TextField(null=True, blank=True)
    enrollment_count = models.IntegerField(null=True, blank=True)
    enrollment_type = models.CharField(max_length=100, null=True, blank=True)
    fda_regulated_drug = models.CharField(max_length=5, choices=FDA_REGULATED_DRUG_CHOICES, default='', blank=True)
    fda_regulated_device = models.CharField(max_length=5, choices=FDA_REGULATED_DEVICE_CHOICES, default='', blank=True)
    primary_outcomes = models.JSONField(null=True, blank=True)
    secondary_outcomes = models.JSONField(null=True, blank=True)
    other_outcomes = models.JSONField(null=True, blank=True)
    clinical_trial_url = models.CharField(max_length=255, null=True, blank=True)
    study_location = models.JSONField(null=True, blank=True)
    genes = models.JSONField(null=True, blank=True)
    eligibility_criteria_generic_description = models.TextField(null=True, blank=True)
    eligibility_criteria_inclusion_description = models.JSONField(null=True, blank=True)
    eligibility_criteria_exclusion_description = models.JSONField(null=True, blank=True)
    eligibility_criteria_healthy_volunteers = models.CharField(max_length=5, choices=ELIGIBILITY_CRITERIA_HEALTHY_VOLUNTEERS_CHOICES, default='', blank=True)
    eligibility_criteria_sex = models.CharField(max_length=255, null=True, blank=True)
    eligibility_criteria_min_age_years = models.CharField(max_length=255, null=True, blank=True)
    eligibility_criteria_max_age_years = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.brief_title

# TODO: Add more fields or models as necessary based on team collabrative input
