import requests
import os
import re
import pandas as pd
from django.conf import settings
from bs4 import BeautifulSoup
from django.db import models
from .models import Trial, Gene
from django.forms.models import model_to_dict
from datetime import datetime
from dateutil import parser
from django.core.exceptions import ValidationError

# This function is designed to update the database with trial and gene data, handling many-to-many relationships appropriately.
# It iterates over each trial, updating or creating trial records, and associates genes by creating or fetching gene records.
# The logic for dynamically using field names from the Trial model minimizes hardcoding and adapts to changes in the model's structure.
def update_data():
    print("Inside update_data function...")
    trials_data = fetch_trial_data()
    print(f"Fetched {len(trials_data)} trial records.")

    unique_ids = {trial['unique_protocol_id'] for trial in trials_data if 'unique_protocol_id' in trial}
    print(f"Number of unique trial IDs: {len(unique_ids)}")

    gene_list_df = scrape_alsod_gene_list()
    print(f"Scraped gene list with {len(gene_list_df)} records.")

    updated_genes = 0
    for _, row in gene_list_df.iterrows():
        gene, created = Gene.objects.update_or_create(
            gene_symbol=row['Gene Symbol'],
            defaults={
                'gene_name': row['Gene Name'], 
                'gene_risk_category': row['Gene Risk Category']
            }
        )
        updated_genes += 1
        if created:
            print(f"Created new gene: {gene.gene_symbol}")
        else:
            print(f"Updated gene: {gene.gene_symbol}")
    print(f"Total genes updated or created: {updated_genes}")

    updated_trials = 0
    for trial_data in trials_data:
        unique_id = trial_data.get('unique_protocol_id')

        if unique_id:
            print(f"Processing trial data for unique ID: {unique_id}")

            # Handling 'NaN' values for numeric fields
            numeric_fields = ['enrollment_count']  # Add more numeric fields as needed
            for field in numeric_fields:
                if pd.isna(trial_data.get(field)):
                    trial_data[field] = None  # Convert 'NaN' to 'None'

            # Adjusting date fields to ensure correct format
            for date_field in ['status_verified_date', 'completion_date']:  # Add or adjust date fields as necessary
                date_value = trial_data.get(date_field)
                if pd.isna(date_value) or date_value in ['', 'nan']:
                    trial_data[date_field] = None
                else:
                    try:
                        parsed_date = parser.parse(str(date_value), default=datetime(1900, 1, 1))
                        trial_data[date_field] = parsed_date.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        print(f"Error parsing {date_field} for trial ID {unique_id}: {date_value}")
                        trial_data[date_field] = None

            defaults = {field.name: trial_data[field.name] for field in Trial._meta.get_fields() if field.name in trial_data and trial_data[field.name] is not None}

            trial_obj, created = Trial.objects.update_or_create(
                unique_protocol_id=unique_id,
                defaults=defaults
            )
            updated_trials += 1

            if 'genes' in trial_data and trial_data['genes']:
                gene_symbols = trial_data['genes'].split(',')
                genes = [Gene.objects.get_or_create(gene_symbol=gene_symbol.strip())[0] for gene_symbol in gene_symbols]
                trial_obj.genes.set(genes)

    print(f"Total trials updated or created: {updated_trials}")
    print("ALS/FTD Research Data has been successfully obtained. Now completing API get.......")
    print("Exiting update_data function...")



# Parses and handles date fields
def parse_date_with_default(date_str, default_date=datetime(1900, 1, 1)):
    """
    Attempts to parse a date string and return it in 'YYYY-MM-DD' format.
    If parsing fails or the input is 'nan', returns None.
    """
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
    trials_data = fetch_trial_data()  # Fetch trial data
    gene_list_df = scrape_alsod_gene_list()  # Scrape gene list to DataFrame

    # Convert gene_list_df to a list of gene symbols for easier processing
    gene_symbols = gene_list_df['Gene Symbol'].tolist()

    for trial in trials_data:
        keywords = trial.get('keyword', '').split(',')
        matched_genes = [gene for gene in gene_symbols if gene in keywords]
        trial['genes'] = matched_genes  # Add matched genes directly to the trial data
    
    return trials_data



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
        # First, aggressively remove all instances of double quotes from the text.
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
    print("Sample scraped gene data:", df.head(1).to_dict())  # Print a sample gene record
    return df



# Converts headers received from API to the shortened name
def denest_field_names(nested_headers):
    denested_headers = []
    for header in nested_headers:
        denested_headers.append(header.split('.')[-1])  # Take the last part after the final dot
    return denested_headers



# This function fetches trial data from ClinicalTrials.gov's API.
# It processes the response, and returns a structured format of trial details.
def fetch_trial_data():
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    query_params = {
        "format": "json",
        "query.cond": "ALS OR FTD OR amyotrophic lateral sclerosis OR frontal lobe dementia",
        "pageSize": 1000,
        "fields": "OrgStudyId|BriefTitle|StudyType|OverallStatus|StatusVerifiedDate|CompletionDate|LeadSponsorName|ResponsiblePartyType|ResponsiblePartyInvestigatorFullName|Condition|Keyword|InterventionName|InterventionDescription|StudyPopulation|EnrollmentCount|EnrollmentType"
    }
    print("Starting fetch_trial_data..before 'all_study_details'...")
    all_studies_details = []
    print("Starting fetch_trial_data")
    try:
        print("About to make API call")
        while True:
            response = requests.get(base_url, params=query_params)
            print("Finished request.get of base_url")
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
                return {"error": "Failed to fetch data", "status_code": response.status_code}
    except Exception as e:
        print("An error occurred:", e)
        return {"error": str(e)}

    # Convert the list of dictionaries to a pandas DataFrame
    df_studies = pd.json_normalize(all_studies_details)
    print("After conversion to DataFrame, headers:", df_studies.columns.tolist())
    if not df_studies.empty:
        print("Sample record after conversion to DataFrame:", df_studies.iloc[0].to_dict())

    # Renaming API column output to match the database model's field names
    column_mappings = {
        "protocolSection.identificationModule.orgStudyIdInfo.id": "unique_protocol_id",
        "protocolSection.identificationModule.briefTitle": "brief_title",
        "protocolSection.designModule.studyType": "study_type",
        "protocolSection.statusModule.overallStatus": "overall_status",
        "protocolSection.statusModule.statusVerifiedDate": "status_verified_date",
        "protocolSection.statusModule.completionDateStruct.date": "completion_date",
        "protocolSection.sponsorCollaboratorsModule.leadSponsor.name": "lead_sponsor_name",
        "protocolSection.sponsorCollaboratorsModule.responsibleParty.type": "responsible_party_type",
        "protocolSection.sponsorCollaboratorsModule.responsibleParty.investigatorFullName": "responsible_party_investigator_full_name",
        "protocolSection.conditionsModule.conditions": "condition",
        "protocolSection.conditionsModule.keywords": "keyword",
        "protocolSection.armsInterventionsModule.interventions": "intervention_name",
        "protocolSection.eligibilityModule.studyPopulation": "study_population",
        "protocolSection.designModule.enrollmentInfo.count": "enrollment_count",
        "protocolSection.designModule.enrollmentInfo.type": "enrollment_type"
    }

    df_studies.rename(columns=column_mappings, inplace=True)
    print("After renaming, headers:", df_studies.columns.tolist())
    if not df_studies.empty:
        print("Sample record after renaming:", df_studies.iloc[0].to_dict())

    # Convert the DataFrame back to a list of dictionaries
    final_studies_details = df_studies.to_dict('records')
    print("Converted back to list of dictionaries. Sample record:", final_studies_details[0] if final_studies_details else "No data")

    return final_studies_details