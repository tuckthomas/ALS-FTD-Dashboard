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
    unique_protocol_id = models.CharField(max_length=255, primary_key=True)  # Primary Key
    brief_title = models.TextField(null=True, blank=True)
    study_type = models.CharField(max_length=255, null=True, blank=True)
    study_phase = models.CharField(max_length=255, null=True, blank=True)
    overall_status = models.CharField(max_length=255, null=True, blank=True)
    study_start_date = models.DateField(null=True, blank=True)
    study_start_date_type = models.CharField(max_length=255, null=True, blank=True)
    status_verified_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    lead_sponsor_name = models.CharField(null=True, max_length=255, blank=True)
    responsible_party_type = models.CharField(null=True, max_length=255)
    responsible_party_investigator_full_name = models.CharField(null=True, max_length=255, blank=True)
    condition = models.TextField(null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    intervention_name = models.TextField(null=True, blank=True)
    study_population = models.TextField(null=True, blank=True)
    enrollment_count = models.IntegerField(null=True, blank=True)
    enrollment_type = models.CharField(max_length=100, null=True, blank=True)
    genes = models.ManyToManyField(Gene, related_name='trials')  # Many-to-Many relationship

    def __str__(self):
        return self.brief_title

# TODO: Add more fields or models as necessary based on team collabrative input
