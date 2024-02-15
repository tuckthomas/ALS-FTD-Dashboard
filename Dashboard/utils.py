import requests
import os
import re
import ast
import pandas as pd
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

    print(f"Total trials updated or created: {updated_trials}")
    print("ALS/FTD Research Data has been successfully obtained. Now completing API get.......")
    print("Exiting update_data function...")


# Attempts to parse a date string and return it in 'YYYY-MM-DD' format.
# If parsing fails or the input is 'nan', returns None.
def parse_date_with_default(date_str, default_date=datetime(1900, 1, 1)):
    if pd.isna(date_str) or date_str in ['', 'nan']:
        return None  # or default_date.strftime("%Y-%m-%d") if you prefer a default date
    try:
        parsed_date = parser.parse(str(date_str), default=default_date)
        return parsed_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None



# This function fetches trial data and enhances it by associating gene symbols based on keywords, using the scraped gene list.
# It prepares the trial data for database updates.
def enhanced_fetch_trial_data():
    # Fetch trial data and print type before conversion
    trials_data_df = fetch_trial_data()
    print(f"Type of trials_data_raw before conversion: {type(trials_data_df).__name__}")

    # Print the first ten records' 'keyword' field
    print("First ten records' 'keyword' field:")
    print(trials_data_df['keyword'].head(10))

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

    # Apply the match_genes function to each row of the trials_data DataFrame.
    trials_data_df['genes'] = trials_data_df.apply(lambda row: match_genes(row, gene_symbols), axis=1)

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

    # Save the DataFrame to a CSV file
    df.to_csv(filepath, index=False)

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
        "fields": "OrgStudyId|BriefTitle|StudyType|OverallStatus|StatusVerifiedDate|CompletionDate|LeadSponsorName|ResponsiblePartyType|ResponsiblePartyInvestigatorFullName|Condition|Keyword|InterventionName|InterventionDescription|StudyPopulation|EnrollmentCount|EnrollmentType|Phase|StartDate|StartDateType"
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
        "protocolSection.identificationModule.orgStudyIdInfo.id": "unique_protocol_id",
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

    # Print the first ten records' 'keyword' field if it exists
    if 'keyword' in df_studies.columns:
        print("First ten records' 'keyword' field:")
        print(df_studies['keyword'].head(10))
    else:
        print("The 'keyword' column does not exist in the DataFrame.")

    # Directly return the DataFrame
    return df_studies
