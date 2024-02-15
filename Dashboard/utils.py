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
from dateutil import parser
from django.core.exceptions import ValidationError

# This function is designed to update the database with trial and gene data, handling many-to-many relationships appropriately.
# It iterates over each trial, updating or creating trial records, and associates genes by creating or fetching gene records.
# The logic for dynamically using field names from the Trial model minimizes hardcoding and adapts to changes in the model's structure.
def update_data():
    print("Inside update_data function...")
    trials_data = enhanced_fetch_trial_data()
    print(f"Fetched {len(trials_data)} trial records (with gene matching).")

    gene_list_df = scrape_alsod_gene_list()  # Fetch the gene list
    print(f"Scraped gene list with {len(gene_list_df)} records.")
    valid_gene_symbols = set(gene_list_df['Gene Symbol'].tolist())

    # Update or create genes in the database from scraped data
    updated_genes = 0
    for _, row in gene_list_df.iterrows():
        Gene.objects.update_or_create(
            gene_symbol=row['Gene Symbol'],
            defaults={
                'gene_name': row['Gene Name'], 
                'gene_risk_category': row['Gene Risk Category']
            }
        )
        updated_genes += 1
    print(f"Total genes updated or created: {updated_genes}")

    updated_trials = 0
    for index, trial_data in trials_data.iterrows():
        unique_id = trial_data['unique_protocol_id']
        if pd.notnull(unique_id):
            print(f"Processing trial data for unique ID: {unique_id}")

            # Handling 'NaN' values for numeric fields and adjusting date fields
            numeric_fields = ['enrollment_count']
            for field in numeric_fields:
                value = trial_data[field]
                if pd.isna(value) or value in ['', 'nan']:
                    trial_data[field] = None
                else:
                    try:
                        trial_data[field] = int(float(value))  # Convert to float first, then to int
                    except ValueError:
                        trial_data[field] = None  # Set to None if conversion fails
                        print(f"Error converting {field} to int for trial ID {unique_id}: {value}")

            date_fields = ['study_submitance_date', 'study_submitance_date_qc', 'study_start_date', 'status_verified_date', 'completion_date']
            for date_field in date_fields:
                date_value = trial_data[date_field]
                if pd.isna(date_value) or date_value in ['', 'nan']:
                    trial_data[date_field] = None
                else:
                    try:
                        parsed_date = parser.parse(str(date_value))
                        trial_data[date_field] = parsed_date.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        print(f"Error parsing {date_field} for trial ID {unique_id}: {date_value}")
                        trial_data[date_field] = None

            # Prepare defaults, ensuring to exclude the 'genes' field
            defaults = {key: value for key, value in trial_data.items() if key != 'genes' and key in [f.name for f in Trial._meta.get_fields()]}

            # Update or create the Trial object
            trial_obj, created = Trial.objects.update_or_create(
                unique_protocol_id=unique_id,
                defaults=defaults
            )
            
            # Handle the 'genes' ManyToManyField separately
            if pd.notnull(trial_data['genes']):
                gene_symbols = trial_data['genes'].split(',')
                genes_to_set = Gene.objects.filter(gene_symbol__in=[gene.strip() for gene in gene_symbols if gene.strip() in valid_gene_symbols])
                trial_obj.genes.set(genes_to_set)
                
            updated_trials += 1
    
    """
    The below portion saves the given data frames into an XLS file with three tabs, and adds a disclosure
    statement to the Dashboard_gene tab. With an accomanying views.py function, this will allow users
    to download the data in XLS format.
    """
    # After processing, fetch data into data frames
    gene_df = pd.DataFrame(list(Gene.objects.all().values()))
    trial_df = pd.DataFrame(list(Trial.objects.all().values()))
    # Generate trial_genes_df using the dedicated function
    trial_genes_df = get_trial_genes_dataframe()
    
    # Now call save_to_xls with these data frames
    save_to_xls(gene_df, trial_df, trial_genes_df)

    print(f"Total trials updated or created: {updated_trials}")



# Obtains the data frame of Clinical Trials/Studies with Gene targets
def get_trial_genes_dataframe():
    trial_genes_data = []
    for trial in Trial.objects.prefetch_related('genes').all():
        for gene in trial.genes.all():
            trial_genes_data.append({
                'trial_id': trial.unique_protocol_id,
                'gene_id': gene.gene_symbol,
            })
    trial_genes_df = pd.DataFrame(trial_genes_data)
    return trial_genes_df



# Populates the dataframes from 'update_data' function into a three-tab XLS file.
def save_to_xls(gene_df, trial_df, trial_genes_df):
    # Create a new Excel workbook
    wb = Workbook()
    
    # Create sheets with the specified order
    ws_trial = wb.active  # First sheet is created by default
    ws_trial.title = "Dashboard_trial"
    ws_gene = wb.create_sheet(title="Dashboard_gene")
    ws_trial_genes = wb.create_sheet(title="Dashboard_trial_genes")
    
    # Populate sheets with data frames
    data_frames = [trial_df, gene_df, trial_genes_df]
    sheets = [ws_trial, ws_gene, ws_trial_genes]
    for df, ws in zip(data_frames, sheets):
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)
    
    # Add disclosure/citation to the Dashboard_gene sheet
    citation_text = "Citation: ALS/FTD gene data has been obtained from https://ALSoD.ac.uk. Updates to variants for many genes in ALSOD since 2015 have been taken from the supplementary material of Emily McCann et al (2021), which has been a valuable resource. Source: https://alsod.ac.uk/acknowledgements.php"
    ws_gene.append([])  # Add an empty row for spacing
    ws_gene.append([citation_text])  # Add the disclosure statement
    
    # Save the workbook to the specified file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'ALS, FTD Clinical Trial Research Data Tables.xlsx')
    wb.save(file_path)
    print(f"File saved to {file_path}")



# This function fetches trial data and enhances it by associating gene symbols based on keywords, using the scraped gene list.
# Additionally, it creates a column for each records ClinicalTrials.gov URL based upon a defined schema.
def enhanced_fetch_trial_data():
    # Fetch trial data and print type before conversion
    trials_data_df = fetch_trial_data()
    print(f"Type of trials_data_raw before conversion: {type(trials_data_df).__name__}")

    gene_list_df = scrape_alsod_gene_list()  # Assume this fetches your gene list correctly
    gene_symbols = gene_list_df['Gene Symbol'].tolist()

    def match_genes(row, gene_symbols):
        # Initialize an empty list for matched genes
        matched_genes = []

        # Check if the 'keyword' field is not null and not empty
        if pd.notnull(row['keyword']) and row['keyword'].strip():
            try:
                # Attempt to safely evaluate the string representation of the list
                keywords_list = ast.literal_eval(row['keyword'])
                if isinstance(keywords_list, list):
                    # Convert both keywords and gene symbols to uppercase for case-insensitive comparison
                    keywords_upper = [keyword.upper() for keyword in keywords_list]
                    matched_genes = [gene for gene in gene_symbols if gene.upper() in keywords_upper]
            except (ValueError, SyntaxError):
                # Log an error or handle it as needed
                print(f"Error parsing keywords for trial {row['unique_protocol_id']}.")
        # No else needed, as matched_genes will remain an empty list if keywords are null, empty, or no matches found

        # Return a comma-separated string of matched genes, or an empty string if none are matched
        return ','.join(matched_genes)

    # Generates the URL for each Study/Trial based upon ClinicalTrial.gov's URL schema
    def clinical_trial_url(nct_id):
        return f"https://clinicaltrials.gov/study/{nct_id}"

    # Apply the match_genes function to each row of the trials_data DataFrame.
    trials_data_df['genes'] = trials_data_df.apply(lambda row: match_genes(row, gene_symbols), axis=1)

    # Add clinical_trial_url column
    trials_data_df['clinical_trial_url'] = trials_data_df['nct_id'].apply(clinical_trial_url)

    return trials_data_df



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
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    query_params = {
        "format": "json",
        "query.cond": "ALS OR FTD OR amyotrophic lateral sclerosis OR frontal lobe dementia",
        "pageSize": 1000,
        "fields": "OrgStudyId|NCTId|BriefTitle|StudyType|OverallStatus|StatusVerifiedDate|CompletionDate|LeadSponsorName|ResponsiblePartyType|ResponsiblePartyInvestigatorFullName|Condition|Keyword|InterventionName|InterventionDescription|StudyPopulation|EnrollmentCount|EnrollmentType|Phase|StartDate|StartDateType|StudyFirstSubmitDate|StudyFirstSubmitQCDate"
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

    # Convert the list of dictionaries to a pandas DataFrame
    df_studies = pd.json_normalize(all_studies_details)
    print("After conversion to DataFrame, headers:", df_studies.columns.tolist())
    if not df_studies.empty:
        print("Sample record after conversion to DataFrame:", df_studies.iloc[0])
        print("DataFrame structure:")
        print(df_studies)

    # Print all column names
    print("Column names:", df_studies.columns)

    # Convert all columns to text
    df_studies = df_studies.astype(str)

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
        "protocolSection.oversightModule.isFdaRegulatedDrug": "fda_reguhlated_drug",
        "protocolSection.oversightModule.isFdaRegulatedDevice": "fda_reguhlated_device"
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
