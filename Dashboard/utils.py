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

# This function is designed to update the database with trial and gene data, handling many-to-many relationships appropriately.
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

        # Update or create the Trial record
        trial_obj, created = Trial.objects.update_or_create(
            unique_protocol_id=row['unique_protocol_id'],
            defaults=defaults
        )
        updated_trials += (1 if created else 0)

    # After processing, fetch data into data frames
    gene_df = pd.DataFrame(list(Gene.objects.all().values()))
    trial_df = pd.DataFrame(list(Trial.objects.all().values()))
    # Now call save_to_xls with these data frames
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
    sheets = [ws_trial, ws_gene, ws_trial_genes]
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
    # Fetch trial data and print type before conversion
    trials_data_df = fetch_trial_data()
    print(f"Type of trials_data_raw before conversion: {type(trials_data_df).__name__}")

    gene_list_df = scrape_alsod_gene_list()  # Assume this fetches your gene list correctly
    gene_symbols = gene_list_df['Gene Symbol'].tolist()

    # Generates the URL for each Study/Trial based upon ClinicalTrial.gov's URL schema
    def clinical_trial_url(nct_id):
        return f"https://clinicaltrials.gov/study/{nct_id}"

    # Create a new DataFrame for processing
    processed_data_df = trials_data_df[['unique_protocol_id', 'keyword']].copy()

    # Convert the 'keyword' field to a text format with commas separating each keyword
    processed_data_df['keyword'] = processed_data_df['keyword'].apply(lambda x: ','.join(x) if isinstance(x, list) else '')

    # Apply the match_genes function to each row of the processed DataFrame.
    processed_data_df['genes'] = processed_data_df.apply(lambda row: match_genes(row, gene_symbols), axis=1)

    # Merge the processed data back into the original DataFrame
    trials_data_df = pd.merge(trials_data_df, processed_data_df[['unique_protocol_id', 'genes']], on='unique_protocol_id', how='left')

    # Add clinical_trial_url column
    trials_data_df['clinical_trial_url'] = trials_data_df['nct_id'].apply(clinical_trial_url)

    # Validate and transform data for choice fields
    trials_data_df['expanded_access'] = trials_data_df['expanded_access'].apply(validate_and_transform_choice_field)
    trials_data_df['fda_regulated_drug'] = trials_data_df['fda_regulated_drug'].apply(validate_and_transform_choice_field)
    trials_data_df['fda_regulated_device'] = trials_data_df['fda_regulated_device'].apply(validate_and_transform_choice_field)

    return trials_data_df


# Data validation for TRUE, FALSE, or BLANK/NULL Choice Fields
def validate_and_transform_choice_field(value):
    # Map the initial capitalized format to the expected uppercase format
    value_map = {
        'True': 'TRUE',
        'False': 'FALSE',
        '': ''
    }
    # Use the value directly if it's in the map; otherwise, return an empty string for invalid or missing inputs
    return value_map.get(value, '')


# This function fetches trial data and enhances it by associating gene symbols based on keywords, using the scraped gene list.
def match_genes(row, gene_symbols):
    valid_keywords_count = 0
    invalid_keywords_count = 0
    matched_genes = []

    # Check if 'keyword' field is not empty and is a valid string
    if isinstance(row['keyword'], str) and row['keyword'].strip():
        try:
            # Split the string by comma and strip each keyword
            keywords_list = [keyword.strip() for keyword in row['keyword'].split(',')]

            # Match keywords with gene symbols ignoring case
            for keyword in keywords_list:
                for gene in gene_symbols:
                    if gene.upper() == keyword.upper():
                        matched_genes.append(gene)
                        valid_keywords_count += 1
                        break  # Break the inner loop once a match is found
                else:
                    invalid_keywords_count += 1
        except (ValueError, TypeError) as e:
            print(f"Error processing keywords for trial {row['unique_protocol_id']}: {e}")
            print("Problematic row data:", row)  # Print the problematic row data
            invalid_keywords_count += 1
    else:
        print(f"Invalid or empty 'keyword' field for trial {row['unique_protocol_id']}")
        invalid_keywords_count += 1

    # Print the total count of records with valid keyword matches
    print(f"Total records with valid keyword matches: {valid_keywords_count}")

    # Serialize matched genes list to JSON string
    print(f"Valid keywords count: {valid_keywords_count}")
    print(f"Invalid/Empty keywords count: {invalid_keywords_count}")
    return json.dumps(matched_genes)






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
        "fields": "OrgStudyId|NCTId|BriefTitle|StudyType|OverallStatus|StatusVerifiedDate|CompletionDate|LeadSponsorName|ResponsiblePartyType|ResponsiblePartyInvestigatorFullName|Condition|Keyword|InterventionName|InterventionDescription|StudyPopulation|EnrollmentCount|EnrollmentType|Phase|StartDate|StartDateType|StudyFirstSubmitDate|StudyFirstSubmitQCDate|HasExpandedAccess|IsFDARegulatedDrug|IsFDARegulatedDevice"
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
        "protocolSection.oversightModule.isFdaRegulatedDevice": "fda_regulated_device"
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
