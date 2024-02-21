import requests
import os
import re
import ast
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from django.conf import settings
from bs4 import BeautifulSoup
from django.db import models
from django.db.models import Q
import numpy as np
from .models import Trial, Gene
from datetime import datetime
from dateutil import parser as date_parser
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
import json

# This function is designed to update the database with trial and gene data.
# It iterates over each trial, updating or creating trial records, and associates genes by creating or fetching gene records.
# The logic for dynamically using field names from the Trial model minimizes hardcoding and adapts to changes in the model's structure.
def update_data():
    print("Inside update_data function...")
    trials_data = enhanced_fetch_trial_data()  # Ensure this returns a DataFrame
    print(f"Fetched {len(trials_data)} trial records (with gene matching).")

    gene_list_df = scrape_alsod_gene_list()  # Fetch the gene list
    print(f"Scraped gene list with {len(gene_list_df)} records.")
    valid_gene_symbols = set(gene_list_df['Gene Symbol'].tolist())

    # Update or create Gene records
    updated_genes = 0
    for _, row in gene_list_df.iterrows():
        _, created = Gene.objects.update_or_create(
            gene_symbol=row['Gene Symbol'],
            defaults={
                'gene_name': row['Gene Name'],
                'gene_risk_category': row['Gene Risk Category']
            }
        )
        updated_genes += (1 if created else 0)
    print(f"Total genes updated or created: {updated_genes}")
    print(gene_list_df.columns)

    updated_trials = 0
    updated_trial_ids = set()  # Collect IDs of trials being updated or created
    # Iterate through each trial record
    for _, row in trials_data.iterrows():
        for date_field in ['study_submitance_date', 'study_submitance_date_qc', 'study_start_date', 'status_verified_date', 'completion_date']:
            if pd.notnull(row[date_field]) and row[date_field].strip():
                try:
                    row[date_field] = date_parser.parse(row[date_field]).date()  # Use dateutil.parser to parse the date
                except ValueError as e:
                    row[date_field] = None  # Reset to None if conversion fails
                    print(f"Error converting date for {date_field} in trial ID {row['unique_protocol_id']}: {e}")
            else:
                row[date_field] = None  # Reset to None if the date field is blank or empty

        # Handling numerical fields
        for num_field in ['enrollment_count']:
            if pd.notnull(row[num_field]) and row[num_field] != '':
                try:
                    row[num_field] = int(row[num_field])
                except ValueError:
                    row[num_field] = None
                    print(f"Error converting {num_field} to int for trial ID {row['unique_protocol_id']}: {row[num_field]}")
            else:
                row[num_field] = None  # Set to None if the value is an empty string

        # Prepare defaults, including JSON serialization for specified fields
        defaults = row.to_dict()
        for json_field in ['genes', 'condition', 'intervention_name', 'keyword']:
            if json_field in defaults and defaults[json_field] not in [None, '']:
                try:
                    defaults[json_field] = json.loads(defaults[json_field]) if isinstance(defaults[json_field], str) else defaults[json_field]
                except json.JSONDecodeError:
                    print(f"Error parsing JSON for {json_field} in trial ID {row['unique_protocol_id']}: {defaults[json_field]}")
                    defaults[json_field] = None
        
        # Add the current trial's unique_protocol_id to the set of processed IDs
        updated_trial_ids.add(row['unique_protocol_id'])
        # Update or create the Trial record
        trial_obj, created = Trial.objects.update_or_create(
            unique_protocol_id=row['unique_protocol_id'],
            defaults=defaults
        )
        updated_trials += (1 if created else 0)

    # Fetch all existing trial IDs from the database
    existing_trial_ids = set(Trial.objects.values_list('unique_protocol_id', flat=True))
    
    # Identify IDs in the database that weren't updated or created in this cycle
    obsolete_trial_ids = existing_trial_ids - updated_trial_ids
    
    # Delete records that are considered obsolete
    if obsolete_trial_ids:
        Trial.objects.filter(unique_protocol_id__in=obsolete_trial_ids).delete()
        print(f"Deleted {len(obsolete_trial_ids)} obsolete trial records.")

    # After processing, fetch data into data frames
    gene_df = pd.DataFrame(list(Gene.objects.all().values()))
    trial_df = pd.DataFrame(list(Trial.objects.all().values()))
    # Call function to save_to_xls with these data frames
    save_to_xls(gene_df, trial_df)

    print(f"Total trials updated or created: {updated_trials}")


# Populates the dataframes from 'update_data' function into a three-tab XLS file.
def save_to_xls(gene_df, trial_df):
    # Create a new Excel workbook
    wb = Workbook()
    
    # Create sheets with the specified order
    ws_trial = wb.active  # First sheet is created by default
    ws_trial.title = "Dashboard_trial"
    ws_gene = wb.create_sheet(title="Dashboard_gene")
    ws_trial_genes = wb.create_sheet(title="Dashboard_trial_genes")
    
    # Populate sheets with data frames
    data_frames = [trial_df, gene_df]
    sheets = [ws_trial, ws_gene]
    for df, ws in zip(data_frames, sheets):
        for r in dataframe_to_rows(df, index=False, header=True):
            # Convert lists to strings before appending to Excel
            converted_row = [str(cell) if isinstance(cell, list) else cell for cell in r]
            ws.append(converted_row)
    
    # Add disclosure/citation to the Dashboard_gene sheet
    citation_text = "Citation: ALS/FTD gene data has been obtained from https://ALSoD.ac.uk. Updates to variants for many genes in ALSOD since 2015 have been taken from the supplementary material of Emily McCann et al (2021), which has been a valuable resource. Source: https://alsod.ac.uk/acknowledgements.php"
    ws_gene.append([])  # Add an empty row for spacing
    ws_gene.append([citation_text])  # Add the disclosure statement
    
    # Save the workbook to the specified file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'ALS, FTD Clinical Trial Research Data Tables.xlsx')
    wb.save(file_path)
    print(f"File saved to {file_path}")




# This function creates a column for the URL of each trial record based upon ClinicalTrial.gov's URL schema.
def enhanced_fetch_trial_data():
    # Fetch trial data
    trials_data_df = fetch_trial_data()
    print(f"Type of trials_data_raw before conversion: {type(trials_data_df).__name__}")

    gene_list_df = scrape_alsod_gene_list()
    gene_symbols = gene_list_df['Gene Symbol'].tolist()
    gene_names = gene_list_df['Gene Name'].tolist()  # Assuming this column exists now
    gene_name_to_symbol = dict(zip(gene_list_df['Gene Name'], gene_list_df['Gene Symbol']))

    # Define the list of field names to be combined
    fields_to_combine = ['keyword', 'condition', 'study_population', 'brief_title']

    # Generates the URL for each Study/Trial based upon ClinicalTrial.gov's URL schema
    def clinical_trial_url(nct_id):
        return f"https://clinicaltrials.gov/study/{nct_id}"

    # Create a new DataFrame for processing that includes the fields defined above
    processed_data_df = trials_data_df[fields_to_combine + ['unique_protocol_id']].copy()

    # Use a lambda function to iterate over the fields_to_combine and process each field accordingly
    processed_data_df['combined_keywords'] = processed_data_df.apply(lambda row: ','.join([','.join(row[field]) if isinstance(row[field], list) else row[field] for field in fields_to_combine]), axis=1)

    # Apply the match_genes function to each row of the processed DataFrame using the combined keywords.
    # Includes gene names and the mapping from gene names to gene symbols as additional parameters
    processed_data_df['genes'] = processed_data_df.apply(lambda row: match_genes(row['combined_keywords'], gene_symbols, gene_names, gene_name_to_symbol), axis=1)

    # Merge the processed data back into the original DataFrame
    trials_data_df = pd.merge(trials_data_df, processed_data_df[['unique_protocol_id', 'genes']], on='unique_protocol_id', how='left')

    # Add clinical_trial_url column
    trials_data_df['clinical_trial_url'] = trials_data_df['nct_id'].apply(clinical_trial_url)

    # Validate and transform data for choice fields
    trials_data_df['expanded_access'] = trials_data_df['expanded_access'].apply(validate_and_transform_choice_field)
    trials_data_df['fda_regulated_drug'] = trials_data_df['fda_regulated_drug'].apply(validate_and_transform_choice_field)
    trials_data_df['fda_regulated_device'] = trials_data_df['fda_regulated_device'].apply(validate_and_transform_choice_field)

    # Convert Study Phase JSONB data to defined mappings
    trials_data_df['study_phase'] = trials_data_df['study_phase'].apply(convert_study_phase)

    return trials_data_df


# Converts study phase data from API.
def convert_study_phase(study_phase_list):
    # Normalize the input list to match the expected format
    normalized_phase_list = [phase.replace('PHASE', 'Phase') for phase in study_phase_list]
    print(f"Normalized study_phase_list: {normalized_phase_list}")  # Debug print

    # Define a mapping from list input to desired output
    phase_mapping = {
        (): 'NA',
        (None,): 'NA',  # Handle None as input, assuming it can be a possible input
        ('NA',): 'NA',
        ('Early_Phase1',): 'Early Phase 1',
        ('Phase1',): 'Phase 1',
        ('Phase1', 'Phase2'): 'Phase 1/2',
        ('Phase2',): 'Phase 2',
        ('Phase2', 'Phase3'): 'Phase 2/3',
        ('Phase3',): 'Phase 3',
    }

    # Convert the normalized input list to a tuple for mapping
    study_phase_key = tuple(normalized_phase_list) if normalized_phase_list else ()

    print(f"Converted study_phase_key: {study_phase_key}")  # Debug print

    # Attempt to get the mapped value
    mapped_value = phase_mapping.get(study_phase_key, 'Unknown')
    
    print(f"Mapped value: {mapped_value}")  # Debug print

    return mapped_value



# Data validation for TRUE, FALSE, or BLANK/NULL Choice Fields
def validate_and_transform_choice_field(value):
    """Transform boolean and 'True'/'False' strings to 'TRUE'/'FALSE', allowing blank fields."""
    # Handle boolean values directly
    if value is True:
        return 'TRUE'
    elif value is False:
        return 'FALSE'
    # Handle string values that are 'true'/'false' (case insensitive)
    elif isinstance(value, str):
        lower_value = value.lower()
        if lower_value == 'true':
            return 'TRUE'
        elif lower_value == 'false':
            return 'FALSE'
        elif value.strip() == '':  # Check for a blank string
            return ''
    # Default case for handling any unexpected value types
    return ''


# This function fetches trial data and enhances it by associating gene symbols based on keywords, using the scraped gene list.
# To refine the matching process and avoid false positives, an additional check occurs to ensure that gene symbols
# are recognized as distinct words or part of a larger keyword that correctly represents
# a gene symbol within the context (e.g., at the beginning of a word, followed by a non-alphabetic character, or at the end of a word). 
def match_genes(combined_keywords, gene_symbols, gene_names, gene_name_to_symbol):
    valid_keywords_count = 0
    invalid_keywords_count = 0
    matched_genes = set()  # Use a set to avoid duplicates

    if isinstance(combined_keywords, str) and combined_keywords.strip():
        try:
            # Split the string by comma and strip each keyword
            keywords_list = [keyword.strip() for keyword in combined_keywords.split(',')]

            # Use regex to match gene symbols and gene names more accurately
            for keyword in keywords_list:
                matched_this_round = False
                for gene_symbol in gene_symbols:
                    # Pattern for gene symbol matches
                    pattern_symbol = rf'\b{gene_symbol}\b|\b{gene_symbol}[^A-Za-z0-9_]|[^A-Za-z0-9_]{gene_symbol}\b'
                    if re.search(pattern_symbol, keyword, re.IGNORECASE):
                        matched_genes.add(gene_symbol)
                        valid_keywords_count += 1
                        matched_this_round = True
                        break  # Break if a gene symbol match is found
                
                if not matched_this_round:
                    for gene_name in gene_names:
                        # Pattern for gene name matches, allowing dashes
                        pattern_name = rf'\b{gene_name}\b'
                        if re.search(pattern_name, keyword, re.IGNORECASE):
                            # Add the gene symbol equivalent for the matched gene name
                            matched_genes.add(gene_name_to_symbol[gene_name])
                            valid_keywords_count += 1
                            matched_this_round = True
                            break  # Break if a gene name match is found

                if not matched_this_round:
                    invalid_keywords_count += 1

        except (ValueError, TypeError) as e:
            print(f"Error processing combined keywords: {e}")
            invalid_keywords_count += 1
    else:
        print("Invalid or empty 'combined_keywords' field")
        invalid_keywords_count += 1

    # Print results for debug purposes
    print(f"Total records with valid keyword matches: {valid_keywords_count}")
    print(f"Valid keywords count: {valid_keywords_count}")
    print(f"Invalid/Empty keywords count: {invalid_keywords_count}")
    return json.dumps(list(matched_genes))  # Convert set back to list for JSON serialization



# This function scrapes gene information from Dr. Al-Chalabi's ALSoD.ac.uk HTML table.
# It processes it into a structured format, ready for database insertion or association with trials, while handling text sanitization.
def scrape_alsod_gene_list():
    url = "https://alsod.ac.uk/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.findAll("tr", class_="clickable-row")

    gene_symbols = []
    gene_names = []
    gene_risk_categories = []

    def sanitize(text):
        # Remove all instances of double quotes from the text.
        text = text.replace('"', '')
        # Remove text within parentheses including the parentheses themselves.
        text = re.sub(r'\(.*?\)', '', text)
        # Normalize whitespace and strip leading/trailing whitespace.
        text = ' '.join(text.split())
        return text

    for row in rows:
        columns = row.findAll("td", class_="assetIDConfig")
         # Ensure there are at least 3 columns for symbol, name, and category
        if len(columns) >= 3:
            # Apply the enhanced sanitize function to each relevant piece of text
            gene_symbol = sanitize(columns[1].text)
            gene_name = sanitize(columns[2].text)
            gene_risk_category = sanitize(columns[3].text)

            gene_symbols.append(gene_symbol)
            gene_names.append(gene_name)
            gene_risk_categories.append(gene_risk_category)

    # Create a DataFrame with the collected data
    df = pd.DataFrame({
        "Gene Symbol": gene_symbols,
        "Gene Name": gene_names,
        "Gene Risk Category": gene_risk_categories
    })

    # Define the filename and the filepath
    filename = 'ALSOD_Gene_List.csv'
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    print("Scraped gene list DataFrame shape:", df.shape)  # Check the shape of the DataFrame
    return df



# This function fetches trial data from ClinicalTrials.gov's API.
# It processes the response, and returns a structured format of trial details.
def fetch_trial_data():
    # ClinicalTrials.gov's API V2 URL.
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    # Conditions to include in search.
    include_conditions = [
        "ALS", "FTD", "amyotrophic lateral sclerosis", 
        "Amyotrophic Lateral Sclerosis", "Motor Neuron Disease", 
        "motor neuron disease", "MND", "mnd", "frontal lobe dementia", 
        "Frontal Lobe Dementia"
    ]

    # Constructing the query condition string.
    # Join include conditions with 'OR'
    query_cond = " OR ".join(include_conditions)

    fields = [
        "OrgStudyId", "NCTId", "BriefTitle", "StudyType", "OverallStatus",
        "StatusVerifiedDate", "CompletionDate", "LeadSponsorName",
        "ResponsiblePartyType", "ResponsiblePartyInvestigatorFullName",
        "Condition", "Keyword", "InterventionName", "InterventionDescription",
        "StudyPopulation", "EnrollmentCount", "EnrollmentType", "Phase",
        "StartDate", "StartDateType", "StudyFirstSubmitDate",
        "StudyFirstSubmitQCDate", "HasExpandedAccess", "IsFDARegulatedDrug",
        "IsFDARegulatedDevice", "Location", "PrimaryOutcome", "SecondaryOutcome",
        "OtherOutcome"
    ]
    query_params = {
        "format": "json",
        "query.cond": query_cond,
        "pageSize": 1000,
        "fields": "|".join(fields)
    }
    print("Starting fetch_trial_data..before 'all_study_details'...")
    all_studies_details = []
    print("Starting fetch_trial_data")
    try:
        print("About to make API call")
        while True:
            response = requests.get(base_url, params=query_params)
            print("Finished request.get of base_url")
            print("Response content:", response.content)
            if response.status_code == 200:
                print("response.status_code == 200....proceed to data = response.json")
                data = response.json()

                studies_details = data.get("studies", [])
                all_studies_details.extend(studies_details)
                # Continues to next 1000 page query due to ClinicalTrials.gov's imposed limitations.
                nextPageToken = data.get("nextPageToken")
                if not nextPageToken:
                    break

                query_params["pageToken"] = nextPageToken
            else:
                print(f"Error: Failed to fetch data. Status code: {response.status_code}")
                return {"error": "Failed to fetch data", "status_code": response.status_code}
    except Exception as e:
        print("An error occurred during API call:", e)
        return {"error": str(e)}

    # False-positive conditions from ClinicalTrials.gov needing excluded from dataset.
    # Different trials often times refer to the same condition using slightly different context.
    # I found some trials misspell the conditions; requiring misspelling of exclusion criteria.
    exclude_conditions = [
        # Spinal Muscular Atrophy
        "Spinal Muscular Atrophy", "spinal muscular atrophy", "Spinal Muscular Atrophy (SMA)",
        "SMA", "Type * Spinal Muscular Atrophy", "Type * SMA",
        "Infantile-onset Spinal Muscular Atrophy", "Infantile-onset SMA",
        "Muscular Atrophy, Spinal, Type *", "Muscular Atrophy, Spinal",
        "Type 2 Spinal Muscular Atrophy", "Spinal Muscular Atrophy 1", "Spinal Muscular Atrophy Type II",
        "Spinal Muscular Atrophy Type III"
        # Primary Progressive Aphasia
        "Aphasia, Primary Progressive", "Primary Progressive Aphasia", "primary progressive aphasia",
        "PPA", "Logopenic Progressive Aphasia", "logopenic progressive aphasia",
        "Nonfluent Variant Primary Progressive Aphasia (nfvPPA)",
        "Logopenic Variant Primary Progressive Aphasia", "Non-fluent Variant Primary Progressive Aphasia",
        "Semantic Variant Primary Progressive Aphasia",
        # Corticobasal Degeneration and Progressive Supranuclear Palsy
        "Corticobasal Degeneration (CBD)", "Corticobasal Syndrome (CBS)", "Cortical-basal Ganglionic Degeneration (CBGD)",
        "Progressive Supranuclear Palsy (PSP)", "Nonfluent Variant Primary Progressive Aphasia (nfvPPA)",
        "Oligosymptomatic/Variant Progressive Supranuclear Palsy (o/vPSP)",
        "CBD", "CBS", "CBGD", "PSP", "nfvPPA", "oPSP", "vPSP", "o/vPSP",
        "Corticobasal Degeneration", "Corticobasal Syndrome", "Cortocal-basal Ganglionic Degeneration",
        "Progressive Supranuclear Palsy", "Oligosymptomatic Progressive Supranuclear Palsy",
        # Niemann-Pick Disease
        "Niemann-Pick Disease", "Neimann-Pick Disease", "Niemann-Pick Disease, Type C", "Niemann-Pick Disease, Type C*",
        "Niemann-Pick Disease, Type C1", "Niemann-Pick Diseases", "Niemann-Pick Disease Type C*", "Pick Disease of the Brain",
        # Other diseases
        "Chronic Lymphocytic Leukemia", "Hurler Syndrome (MPS I)", "Hurler-Scheie Syndrome", "Hunter Syndrome (MPS II)",
        "Sanfilippo Syndrome (MPS III)", "Krabbe Disease (Globoid Leukodystrophy)", "Metachromatic Leukodystrophy",
        "Adrenoleukodystrophy (ALD and AMN)", "Sandhoff Disease", "Tay Sachs Disease", "Pelizaeus Merzbacher (PMD)",
        "Alpha-mannosidosis", "Juvenile Neuronal Ceroid Lipofuscinosis", "Smith-Lemli-Opitz Syndrome",
        "Creatine Transporter Deficiency", "Mucopolysaccharidosis I", "Mucopolysaccharidosis VI", "Adrenoleukodystrophy",
        "Metachromatic Leukodystrophy", "Wolman Disease", "Krabbe's Disease", "Gaucher's Disease", "Fucosidosis",
        "Batten Disease", "Severe Aplastic Anemia", "Diamond-Blackfan Anemia", "Amegakaryocytic Thrombocytopenia",
        "Myelodysplastic Syndrome", "Acute Myelogenous Leukemia", "Acute Lymphocytic Leukemia", "Lysosomal Acid Lipase Deficiency",
        "Stroke", "Spasticity", "Acid Sphingomyelinase Deficiency", "Gaucher Disease", "ASMD", "Splenomegaly",
        "Colorectal Neoplasms", "Trifluridine and Tipiracil", "Circulating Tumor DNA", "Satisfaction", "Nonalcoholic Steatohepatitis",
        "Prostate Cancer", "Renal Cancer", "Brain Cancer", "Feasibility of Neonatal Screening for Spinal Amyotrophy", "Diplegic Cerebral Palsy",
        "Rare Disorders", "Undiagnosed Disorders", "Disorders of Unknown Prevalence", "Cornelia De Lange Syndrome",
        "Prenatal Benign Hypophosphatasia", "Perinatal Lethal Hypophosphatasia", "Odontohypophosphatasia", "Adult Hypophosphatasia",
        "Childhood-onset Hypophosphatasia", "Infantile Hypophosphatasia", "Hypophosphatasia", "Kabuki Syndrome",
        "Bohring-Opitz Syndrome", "Narcolepsy Without Cataplexy", "Narcolepsy-cataplexy", "Hypersomnolence Disorder",
        "Idiopathic Hypersomnia Without Long Sleep Time", "Idiopathic Hypersomnia With Long Sleep Time", "Idiopathic Hypersomnia",
        "Kleine-Levin Syndrome", "Kawasaki Disease", "Leiomyosarcoma", "Leiomyosarcoma of the Corpus Uteri",
        "Leiomyosarcoma of the Cervix Uteri", "Leiomyosarcoma of Small Intestine", "Acquired Myasthenia Gravis",
        "Addison Disease", "Hyperacusis (Hyperacousis)", "Juvenile Myasthenia Gravis", "Transient Neonatal Myasthenia Gravis",
        "Williams Syndrome", "Lyme Disease", "Myasthenia Gravis", "Marinesco Sjogren Syndrome(Marinesco-Sjogren Syndrome)",
        "Isolated Klippel-Feil Syndrome", "Frasier Syndrome", "Denys-Drash Syndrome", "Beckwith-Wiedemann Syndrome",
        "Emanuel Syndrome", "Isolated Aniridia", "Axenfeld-Rieger Syndrome", "Aniridia-intellectual Disability Syndrome",
        "Aniridia - Renal Agenesis - Psychomotor Retardation", "Aniridia - Ptosis - Intellectual Disability - Familial Obesity",
        "Aniridia - Cerebellar Ataxia - Intellectual Disability", "Aniridia - Absent Patella", "Aniridia",
        "Peters Anomaly - Cataract", "Peters Anomaly", "Potocki-Shaffer Syndrome",
        "Silver-Russell Syndrome Due to Maternal Uniparental Disomy of Chromosome 11",
        "Silver-Russell Syndrome Due to Imprinting Defect of 11p15", "Silver-Russell Syndrome Due to 11p15 Microduplication",
        "Syndromic Aniridia", "WAGR Syndrome", "Wolf-Hirschhorn Syndrome", "4p16.3 Microduplication Syndrome",
        "4p Deletion Syndrome, Non-Wolf-Hirschhorn Syndrome", "Autosomal Recessive Stickler Syndrome",
        "Stickler Syndrome Type *", "Stickler Syndrome", "Mucolipidosis Type 4", "X-linked Spinocerebellar Ataxia Type *",
        "X-linked Intellectual Disability - Ataxia - Apraxia", "Vitamin B12 Deficiency Ataxia", "Toxic Exposure Ataxia",
        "Unclassified Autosomal Dominant Spinocerebellar Ataxia", "Thyroid Antibody Ataxia", "Sporadic Adult-onset Ataxia of Unknown Etiology",
        "Spinocerebellar Ataxia With Oculomotor Anomaly", "Spinocerebellar Ataxia With Epilepsy", "Spinocerebellar Ataxia With Axonal Neuropathy Type *",
        "Spinocerebellar Ataxia Type *", "Spinocerebellar Ataxia - Unknown", "Spinocerebellar Ataxia - Dysmorphism",
        "Non Progressive Epilepsy and/or Ataxia With Myoclonus as a Major Feature", "Spasticity-ataxia-gait Anomalies Syndrome",
        "Spastic Ataxia With Congenital Miosis", "Spastic Ataxia - Corneal Dystrophy", "Spastic Ataxia", "Rare Hereditary Ataxia",
        "Rare Ataxia", "Recessive Mitochondrial Ataxia Syndrome", "Progressive Epilepsy and/or Ataxia With Myoclonus as a Major Feature",
        "Posterior Column Ataxia - Retinitis Pigmentosa", "Post-Stroke Ataxia", "Post-Head Injury Ataxia", "Post Vaccination Ataxia",
        "Polyneuropathy - Hearing Loss - Ataxia - Retinitis Pigmentosa - Cataract", "Muscular Atrophy - Ataxia - Retinitis Pigmentosa - Diabetes Mellitus",
        "Non-hereditary Degenerative Ataxia", "Paroxysmal Dystonic Choreathetosis With Episodic Ataxia and Spasticity",
        "Olivopontocerebellar Atrophy - Deafness", "NARP Syndrome", "Myoclonus - Cerebellar Ataxia - Deafness",
        "Multiple System Atrophy, Parkinsonian Type", "Multiple System Atrophy, Cerebellar Type", "Multiple System Atrophy",
        "Maternally-inherited Leigh Syndrome", "Machado-Joseph Disease Type *", "Leigh Syndrome", "Late-onset Ataxia With Dementia",
        "Infection or Post Infection Ataxia", "GAD Ataxia", "Hereditary Episodic Ataxia", "Gliadin/Gluten Ataxia",
        "Friedreich Ataxia", "Fragile X-associated Tremor/Ataxia Syndrome", "Familial Paroxysmal Ataxia",
        "Exposure to Medications Ataxia", "Episodic Ataxia With Slurred Speech", "Episodic Ataxia Unknown Type",
        "Epilepsy and/or Ataxia With Myoclonus as Major Feature", "Early-onset Spastic Ataxia-neuropathy Syndrome",
        "Early-onset Progressive Neurodegeneration - Blindness - Ataxia - Spasticity",
        "Early-onset Cerebellar Ataxia With Retained Tendon Reflexes", "Early-onset Ataxia With Dementia",
        "Childhood-onset Autosomal Recessive Slowly Progressive Spinocerebellar Ataxia", "Dilated Cardiomyopathy With Ataxia",
        "Cataract - Ataxia - Deafness", "Cerebellar Ataxia, Cayman Type", "Cerebellar Ataxia With Peripheral Neuropathy",
        "Cerebellar Ataxia - Hypogonadism", "Cerebellar Ataxia - Ectodermal Dysplasia",
        "Cerebellar Ataxia - Areflexia - Pes Cavus - Optic Atrophy - Sensorineural Hearing Loss", "Brain Tumor Ataxia",
        "Brachydactyly - Nystagmus - Cerebellar Ataxia", "Benign Paroxysmal Tonic Upgaze of Childhood With Ataxia",
        "Autosomal Recessive Syndromic Cerebellar Ataxia", "Autosomal Recessive Spastic Ataxia With Leukoencephalopathy",
        "Autosomal Recessive Spastic Ataxia of Charlevoix-Saguenay",
        "Autosomal Recessive Spastic Ataxia - Optic Atrophy - Dysarthria", "Autosomal Recessive Spastic Ataxia",
        "Autosomal Recessive Metabolic Cerebellar Ataxia",
        "Autosomal Dominant Spinocerebellar Ataxia Due to Repeat Expansions That do Not Encode Polyglutamine",
        "Autosomal Recessive Ataxia, Beauce Type", "Autosomal Recessive Ataxia Due to Ubiquinone Deficiency",
        "Autosomal Recessive Ataxia Due to PEX10 Deficiency",
        "Autosomal Recessive Degenerative and Progressive Cerebellar Ataxia",
        "Autosomal Recessive Congenital Cerebellar Ataxia Due to MGLUR1 Deficiency",
        "Autosomal Recessive Congenital Cerebellar Ataxia Due to GRID2 Deficiency",
        "Autosomal Recessive Congenital Cerebellar Ataxia",
        "Autosomal Recessive Cerebellar Ataxia-pyramidal Signs-nystagmus-oculomotor Apraxia Syndrome",
        "Autosomal Recessive Cerebellar Ataxia-epilepsy-intellectual Disability Syndrome Due to WWOX Deficiency",
        "Autosomal Recessive Cerebellar Ataxia-epilepsy-intellectual Disability Syndrome Due to TUD Deficiency",
        "Autosomal Recessive Cerebellar Ataxia-epilepsy-intellectual Disability Syndrome Due to KIAA0226 Deficiency",
        "Autosomal Recessive Cerebellar Ataxia-epilepsy-intellectual Disability Syndrome",
        "Autosomal Recessive Cerebellar Ataxia With Late-onset Spasticity", "Autosomal Recessive Cerebellar Ataxia Due to STUB1 Deficiency",
        "Autosomal Recessive Cerebellar Ataxia Due to a DNA Repair Defect",
        "Autosomal Recessive Cerebellar Ataxia - Saccadic Intrusion",
        "Autosomal Recessive Cerebellar Ataxia - Psychomotor Retardation",
        "Autosomal Recessive Cerebellar Ataxia - Blindness - Deafness", "Autosomal Recessive Cerebellar Ataxia",
        "Autosomal Dominant Spinocerebellar Ataxia Due to a Polyglutamine Anomaly",
        "Autosomal Dominant Spinocerebellar Ataxia Due to a Point Mutation",
        "Autosomal Dominant Spinocerebellar Ataxia Due to a Channelopathy",
        "Autosomal Dominant Spastic Ataxia Type *", "Autosomal Dominant Spastic Ataxia", "Autosomal Dominant Optic Atrophy",
        "Ataxia-telangiectasia Variant", "Ataxia-telangiectasia",
        "Autosomal Dominant Cerebellar Ataxia, Deafness and Narcolepsy", "Autosomal Dominant Cerebellar Ataxia Type *",
        "Ataxia-telangiectasia-like Disorder", "Ataxia With Vitamin E Deficiency", "Ataxia With Dementia",
        "Ataxia - Oculomotor Apraxia Type 1", "Ataxia - Other", "Ataxia - Genetic Diagnosis - Unknown", "Acquired Ataxia",
        "Adult-onset Autosomal Recessive Cerebellar Ataxia", "Alcohol Related Ataxia", "Multiple Endocrine Neoplasia",
        "Multiple Endocrine Neoplasia Type *", "Atypical Hemolytic Uremic Syndrome", "Atypical HUS", "Wiedemann-Steiner Syndrome",
        "Breast Implant-Associated Anaplastic Large Cell Lymphoma", "Autoimmune/Inflammatory Syndrome Induced by Adjuvants (ASIA)",
        "Hemophagocytic Lymphohistiocytosis", "Behcet's Disease", "Alagille Syndrome",
        "Inclusion Body Myopathy With Early-onset Paget Disease and Frontotemporal Dementia (IBMPFD)", "Lowe Syndrome", "Pitt Hopkins Syndrome",
        "1p36 Deletion Syndrome", "Jansen Type Metaphyseal Chondrodysplasia", "Cockayne Syndrome", "Chronic Recurrent Multifocal Osteomyelitis",
        "CRMO", "Malan Syndrome", "Hereditary Sensory and Autonomic Neuropathy Type *", "VCP Disease", "Hypnic Jerking", "Sleep Myoclonus",
        "Mollaret Meningitis", "Recurrent Viral Meningitis", "CRB1", "Leber Congenital Amaurosis", "Retinitis Pigmentosa",
        "Rare Retinal Disorder", "KCNMA1-Channelopathy", "Primary Biliary Cirrhosis", "ZMYND11", "Transient Global Amnesia",
        "Glycogen Storage Disease", "Alstrom Syndrome", "White Sutton Syndrome", "DNM1", "EIEE*", "Myhre Syndrome",
        "Recurrent Respiratory Papillomatosis", "Laryngeal Papillomatosis", "Tracheal Papillomatosis", "Refsum Disease",
        "Nicolaides Baraitser Syndrome", "Leukodystrophy", "Tango*", "Cauda Equina Syndrome", "Rare Gastrointestinal Disorders",
        "Achalasia-Addisonian Syndrome", "Achalasia Cardia", "Achalasia Icrocephaly Syndrome", "Anal Fistula",
        "Congenital Sucrase-Isomaltase Deficiency", "Eosinophilic Gastroenteritis", "Idiopathic Gastroparesis", "Hirschsprung Disease",
        "Rare Inflammatory Bowel Disease", "Intestinal Pseudo-Obstruction", "Scleroderma", "Short Bowel Syndrome", "Sacral Agenesis",
        "Sacral Agenesis Syndrome", "Caudal Regression", "Scheuermann Disease", "SMC1A Truncated Mutations (Causing Loss of Gene Function)",
        "Cystinosis", "Juvenile Nephropathic Cystinosis", "Nephropathic Cystinosis", "Kennedy Disease", "Spinal Bulbar Muscular Atrophy",
        "Warburg Micro Syndrome", "Mucolipidoses", "Mitochondrial Diseases", "Mitochondrial Aminoacyl-tRNA Synthetases",
        "Mt-aaRS Disorders", "Hypertrophic Olivary Degeneration", "Non-Ketotic Hyperglycinemia", "Fish Odor Syndrome", "Halitosis",
        "Isolated Congenital Asplenia", "Lambert Eaton (LEMS)", "Biliary Atresia", "STAG1 Gene Mutation", "Coffin Lowry Syndrome",
        "Borjeson-Forssman-Lehman Syndrome", "Blau Syndrome", "Arginase 1 Deficiency", "HSPB8 Myopathy", "Beta-Mannosidosis",
        "TBX4 Syndrome", "DHDDS Gene Mutations", "MAND-MBD5-Associated Neurodevelopmental Disorder", "Constitutional Mismatch Repair Deficiency (CMMRD)",
        "SPATA5 Disorder", "SPATA5L* Related Disorder", "Kennedy's Disease", "Sialorrhea", "Fibromyalgia", "Fertility Issues", "Asmd, Visceral Type",
        "Sphingomyelin Lipidosis", "Cholangiocarcinoma", "Stage III Gallbladder Cancer AJCC v7", "Stage IIIA Gallbladder Cancer AJCC v7",
        "Stage IIIB Gallbladder Cancer AJCC v7", "Stage IV Gallbladder Cancer AJCC v7", "Stage IVA Gallbladder Cancer AJCC v7",
        "Stage IVB Gallbladder Cancer AJCC v7", "Hemiplegic Cerebral Palsy", "Tetraplegia", "Psychiatric Adults Patients"
    ]

    # Post-processing to exclude trials based on exclusion criteria, referencing the nested field name for 'conditions'
    filtered_studies_details = []
    for study in all_studies_details:
        # Extracts the list of conditions for the study
        study_conditions = study.get('protocolSection', {}).get('conditionsModule', {}).get('conditions', [])
        # Checks if any of the study conditions match any of the exclusion criteria
        if not any(excl_condition.lower() in [cond.lower() for cond in study_conditions] for excl_condition in exclude_conditions):
            filtered_studies_details.append(study)

    # Converts to DataFrame for further processing
    df_studies = pd.json_normalize(filtered_studies_details)

    print("After conversion to DataFrame, headers:", df_studies.columns.tolist())
    if not df_studies.empty:
        print("Sample record after conversion to DataFrame:", df_studies.iloc[0])
        print("DataFrame structure:")
        print(df_studies)

    # Print all column names
    print("Column names:", df_studies.columns)

    # Replace 'nan' strings with actual NaN values
    df_studies.replace('nan', np.nan, inplace=True)

    # Fill missing values with an empty string
    df_studies.fillna('', inplace=True)

    # Renaming API column output to match the database model's field names
    column_mappings = {
        "protocolSection.identificationModule.orgStudyIdInfo.id": "unique_protocol_id", # Primary Key from models.py
        "protocolSection.identificationModule.nctId": "nct_id",
        "protocolSection.identificationModule.briefTitle": "brief_title",
        "protocolSection.designModule.studyType": "study_type",
        "protocolSection.designModule.phases": "study_phase",
        "protocolSection.statusModule.overallStatus": "overall_status",
        "protocolSection.statusModule.studyFirstSubmitDate": "study_submitance_date",
        "protocolSection.statusModule.studyFirstSubmitQcDate": "study_submitance_date_qc",
        "protocolSection.statusModule.startDateStruct.date": "study_start_date",
        "protocolSection.statusModule.startDateStruct.type": "study_start_date_type",
        "protocolSection.statusModule.statusVerifiedDate": "status_verified_date",
        "protocolSection.statusModule.completionDateStruct.date": "completion_date",
        "protocolSection.sponsorCollaboratorsModule.leadSponsor.name": "lead_sponsor_name",
        "protocolSection.sponsorCollaboratorsModule.responsibleParty.type": "responsible_party_type",
        "protocolSection.sponsorCollaboratorsModule.responsibleParty.investigatorFullName": "responsible_party_investigator_full_name",
        "protocolSection.conditionsModule.conditions": "condition",
        "protocolSection.sponsorCollaboratorsModule.collaborators": "collaborators",
        "protocolSection.conditionsModule.keywords": "keyword",
        "protocolSection.armsInterventionsModule.interventions": "intervention_name",
        "protocolSection.eligibilityModule.studyPopulation": "study_population",
        "protocolSection.designModule.enrollmentInfo.count": "enrollment_count",
        "protocolSection.designModule.enrollmentInfo.type": "enrollment_type",
        "protocolSection.statusModule.expandedAccessInfo.hasExpandedAccess": "expanded_access",
        "protocolSection.oversightModule.isFdaRegulatedDrug": "fda_regulated_drug",
        "protocolSection.contactsLocationsModule.locations": "study_location",
        "protocolSection.oversightModule.isFdaRegulatedDevice": "fda_regulated_device",
        "protocolSection.outcomesModule.primaryOutcomes": "primary_outcomes",
        "protocolSection.outcomesModule.secondaryOutcomes": "secondary_outcomes",
        "protocolSection.outcomesModule.otherOutcomes": "other_outcomes"
    }

    df_studies.rename(columns=column_mappings, inplace=True)
    print("After renaming, headers:", df_studies.columns.tolist())
    if not df_studies.empty:
        print("Sample record after renaming:", df_studies.iloc[0])

    # Print the first ten records' 'nct_id' field if it exists
    if 'nct_id' in df_studies.columns:
        print("First ten records' 'nct_id' field:")
        print(df_studies['nct_id'].head(50))
    else:
        print("The 'nct_id' column does not exist in the DataFrame.")

    # Directly return the DataFrame
    return df_studies
