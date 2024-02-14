from django.http import JsonResponse
import requests
import csv
import os
import re
import pandas as pd
from django.conf import settings
from bs4 import BeautifulSoup
from django.http import HttpResponse, response

# Consolidated Function
def process_and_save_trials_data(request):
    # Step 1: Fetch the trial data
    trial_data = fetch_trial_data()

    # Step 2: Scrape the ALSOD gene list
    gene_list_df = scrape_alsod_gene_list()

    # Step 3: Enhance the trial data with 'Mutation/Target' column
    trial_data_with_mutation_target = create_mutation_target_column(trial_data, gene_list_df)

    # Step 4: Save the enhanced DataFrame to CSV
    filename = 'enhanced_trials_data.csv'
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    trial_data_with_mutation_target.to_csv(filepath, index=False)

    return JsonResponse({"message": "Enhanced trial data successfully saved to CSV", "filename": filename})

# Scraps Dr. Al-Chalabi's ALSoD HTML table containing Gene Symbols, Gene Names, and their Risk Category
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

    return pd.DataFrame({
        "Gene Symbol": gene_symbols,
        "Gene Name": gene_names,
        "Gene Risk Category": gene_risk_categories
    })

# API Fetch Request of ClinicalTrials.gov V2 API
def fetch_trial_data():
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    query_params = {
        "format": "json",
        "query.cond": "ALS OR FTD OR amyotrophic lateral sclerosis OR frontal lobe dementia",
        "pageSize": 1000,
        "fields": "BriefTitle|StudyType|OverallStatus|StatusVerifiedDate|CompletionDate|LeadSponsorName|ResponsiblePartyType|ResponsiblePartyInvestigatorFullName|Condition|Keyword|InterventionName|InterventionDescription|StudyPopulation|EnrollmentCount|EnrollmentType"
    }

    all_studies_details = []
    try:
        while True:
            response = requests.get(base_url, params=query_params)
            if response.status_code == 200:
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
        return {"error": str(e)}

    return pd.json_normalize(all_studies_details)

# Parses 'Keyword' field from API data using the Gene Symbold from ALSoD data
def create_mutation_target_column(df_trials, df_gene_list):
    # Handle null/blank values for 'protocolSection.conditionsModule.keywords'
    column_name = 'protocolSection.conditionsModule.keywords'
    if column_name not in df_trials.columns:
        df_trials[column_name] = ''  # Add column with empty strings if it doesn't exist
    else:
        df_trials[column_name].fillna('', inplace=True)  # Replace null values with empty strings

    df_trials[column_name] = df_trials[column_name].astype(str)
    df_trials['Mutation/Target'] = ''

    for index, row in df_gene_list.iterrows():
        gene_symbol = row['Gene Symbol']
        # Now correctly using the full field name for string operations
        mask = df_trials[column_name].str.contains(gene_symbol, case=False, regex=False)
        df_trials.loc[mask, 'Mutation/Target'] = df_trials.loc[mask, 'Mutation/Target'] + gene_symbol + ','

    # Remove trailing commas from the 'Mutation/Target' column
    df_trials['Mutation/Target'] = df_trials['Mutation/Target'].str.rstrip(',')

    return df_trials