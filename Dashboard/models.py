from django.db import models
from django.contrib.postgres.fields import JSONField

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

# Normalized Status Model
class TrialStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

# Model for ClinicalTrials.gov Data
class Trial(models.Model):
    # Choices definitions remain the same...
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
    brief_description = models.TextField(null=True, blank=True)
    study_type = models.CharField(max_length=255, null=True, blank=True)
    study_phase = models.CharField(max_length=50, null=True, blank=True)
    overall_status = models.CharField(max_length=255, null=True, blank=True)
    status = models.ManyToManyField(TrialStatus, related_name='trials', blank=True) # New normalized relation
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
    related_genes = models.ManyToManyField(Gene, related_name='trials', blank=True)

    eligibility_criteria_generic_description = models.TextField(null=True, blank=True)
    eligibility_criteria_inclusion_description = models.JSONField(null=True, blank=True)
    eligibility_criteria_exclusion_description = models.JSONField(null=True, blank=True)
    eligibility_criteria_healthy_volunteers = models.CharField(max_length=5, choices=ELIGIBILITY_CRITERIA_HEALTHY_VOLUNTEERS_CHOICES, default='', blank=True)
    eligibility_criteria_sex = models.CharField(max_length=255, null=True, blank=True)
    eligibility_criteria_min_age_years = models.CharField(max_length=255, null=True, blank=True)
    eligibility_criteria_max_age_years = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.brief_title

# Flattens the Intervention_Name field from ClinicalTrials.gov API data
class Intervention(models.Model):
    trial = models.ForeignKey(Trial, related_name='interventions', on_delete=models.CASCADE)
    intervention_name = models.CharField(max_length=500, null=True, blank=True)
    intervention_type = models.CharField(max_length=255)
    intervention_description = models.TextField()

# Model for Healey Platform Trial; to be merged into singular Trial model at later date
class HealeyTrial(models.Model):
    facility = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    enrollment_status = models.CharField(max_length=255, blank=True, null=True)
    trial_contact_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.facility}, {self.state}, {self.country}"

# User Contact/Feedback Submissions
class ContactSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.email}"

# Issue/Bug Reports
class IssueReport(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    steps_to_reproduce = models.TextField(blank=True, null=True)
    browser_info = models.CharField(max_length=255, blank=True, null=True)
    reported_by = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='open') # open, in_progress, resolved

    def __str__(self):
        return self.title

# ALS/FTD News Articles
class NewsArticle(models.Model):
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True) # Full content if available
    source_name = models.CharField(max_length=255) # e.g., "ALS News Today", "Nature"
    url = models.URLField(unique=True, max_length=2000)
    image_url = models.URLField(blank=True, null=True, max_length=2000)
    publication_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.JSONField(default=list, blank=True) # e.g., ["Research", "Clinical Trial", "ALS"]
    related_genes = models.ManyToManyField(Gene, related_name='news_articles', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publication_date']


# 3D Structure data for genes
class GeneStructure(models.Model):
    SOURCE_PDB = 'pdb'
    SOURCE_ALPHAFOLD = 'alphafold'
    SOURCE_CHOICES = [
        (SOURCE_PDB, 'PDB'),
        (SOURCE_ALPHAFOLD, 'AlphaFold'),
    ]

    gene = models.ForeignKey(Gene, on_delete=models.CASCADE, related_name='structures')
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    external_id = models.CharField(max_length=50)  # PDB ID or UniProt accession
    title = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    visual_style = models.CharField(max_length=50, blank=True, default='cartoon')
    hide_controls = models.BooleanField(default=True)
    alphafold_view = models.BooleanField(default=False)
    custom_data_url = models.URLField(blank=True, null=True, max_length=500)
    custom_data_format = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        unique_together = ['gene', 'source_type', 'external_id']

    def __str__(self):
        return f"{self.gene.gene_symbol} - {self.source_type}:{self.external_id}"

    def get_component_props(self):
        """Returns props for the pdbe-molstar web component."""
        props = {
            'visual-style': self.visual_style or 'cartoon',
            'hide-controls': 'true' if self.hide_controls else 'false',
            'bg-color-r': '0', 'bg-color-g': '0', 'bg-color-b': '0',
        }
        if self.source_type == self.SOURCE_PDB:
            props['molecule-id'] = self.external_id.lower()
        elif self.custom_data_url:
            props['custom-data-url'] = self.custom_data_url
            props['custom-data-format'] = self.custom_data_format or 'cif'
        return props
