from django.db import models

# Model for Gene List Information
class Gene(models.Model):
    gene_symbol = models.CharField(max_length=255)
    gene_name = models.CharField(max_length=255)
    gene_risk_category = models.CharField(max_length=255)

    def __str__(self):
        return self.gene_symbol

# Model for ClinicalTrials.gov Data
class Trial(models.Model):
    EXPANDED_ACCESS_CHOICES = [
        ('TRUE', 'True'),
        ('FALSE', 'False'),
        ('', '')
    ]

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

    unique_protocol_id = models.CharField(max_length=255, primary_key=True)  # Primary Key
    nct_id = models.CharField(max_length=255)
    brief_title = models.TextField(null=True, blank=True)
    study_type = models.CharField(max_length=255, null=True, blank=True)
    study_phase = models.CharField(max_length=255, null=True, blank=True)
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
    intervention_name = models.JSONField(null=True, blank=True)
    study_population = models.TextField(null=True, blank=True)
    enrollment_count = models.IntegerField(null=True, blank=True)
    enrollment_type = models.CharField(max_length=100, null=True, blank=True)
    expanded_access = models.CharField(max_length=5, choices=EXPANDED_ACCESS_CHOICES, default='', blank=True)
    fda_regulated_drug = models.CharField(max_length=5, choices=FDA_REGULATED_DRUG_CHOICES, default='', blank=True)
    fda_regulated_device = models.CharField(max_length=5, choices=FDA_REGULATED_DEVICE_CHOICES, default='', blank=True)
    clinical_trial_url = models.CharField(max_length=255, null=True, blank=True)
    genes = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.brief_title

# TODO: Add more fields or models as necessary based on team collabrative input
