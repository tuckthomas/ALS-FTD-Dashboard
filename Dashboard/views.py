from django.http import JsonResponse
import requests
import csv
import os
import re
import pandas as pd
from django.conf import settings
from bs4 import BeautifulSoup
from django.http import HttpResponse

# Scrap ALSoD website to obtain gene symbols, names, and risk categories. Will be used later to parse ClinicalTrials.gov API 'Keywords' field to create custom filter option based upon gene mutation.
def scrape_alsod_gene_list(request):
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
        if len(columns) >= 3:  # Ensure there are at least 3 columns for symbol, name, and category
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

    return HttpResponse(f"Gene list successfully scraped and saved to {filename}")

def fetch_trials(request):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    query_params = {
        "format": "json",
        "query.cond": "ALS OR FTD OR amyotrophic lateral sclerosis OR frontal lobe dementia",
        "pageSize": 1000,  # ClinicalTrials.gov's per page limitation
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

                print(f"Fetched {len(studies_details)} studies details successfully.")

                # Pagination: Check for nextPageToken in the response to fetch the next batch of studies
                nextPageToken = data.get("nextPageToken")
                if not nextPageToken:
                    print("No more pages to fetch.")
                    break  # No more pages, exit the loop
                
                query_params["pageToken"] = nextPageToken
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
                return JsonResponse({"error": "Failed to fetch data", "status_code": response.status_code}, status=response.status_code)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
    
    print(f"Total fetched studies details: {len(all_studies_details)}")
    return JsonResponse(all_studies_details, safe=False)

def fetch_trials_csv(request):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    query_params = {
        "format": "json",
        "query.cond": "ALS OR FTD OR amyotrophic lateral sclerosis OR frontal lobe dementia",
        "pageSize": 1000,  # ClinicalTrials.gov's per page limitation
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
                    break  # No more pages

                query_params["pageToken"] = nextPageToken
            else:
                return JsonResponse({"error": "Failed to fetch data", "status_code": response.status_code}, status=response.status_code)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    # Convert the list of dictionaries to a DataFrame
    df = pd.json_normalize(all_studies_details)
    
    # Define the filename and path to save the CSV file
    filename = 'trials_data.csv'
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    
    # Save the DataFrame to a CSV file
    df.to_csv(filepath, index=False)
    
    return JsonResponse({"message": "Data successfully saved to CSV", "filename": filepath})

