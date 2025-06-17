import requests
import time
import os
import pandas as pd

# === SETUP ===
EMAIL = " "     # Put your email here
CSV_PATH = "extracted_dois.csv"  # Path to the CSV file containing DOIs or whatever
PDF_DIR = "ref_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# === LOAD DOIs ===
df = pd.read_csv(CSV_PATH)
dois = df['DOI'].dropna().unique()

# === DEFINE FUNCTIONS ===

def get_pdf_url(doi):
    """Check Unpaywall for OA PDF URL"""
    api_url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            location = data.get("best_oa_location", {})
            return location.get("url_for_pdf")
    except Exception as e:
        print(f"Error fetching {doi}: {e}")
    return None

def download_pdf(pdf_url, filename):
    """Download PDF from URL"""
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded: {filename}")
            return True
    except Exception as e:
        print(f"❌ Failed to download {pdf_url}: {e}")
    return False

# === MAIN LOOP ===

for doi in dois:
    print(f"🔎 Checking DOI: {doi}")
    pdf_url = get_pdf_url(doi)
    if pdf_url:
        filename = os.path.join(PDF_DIR, doi.replace("/", "_") + ".pdf")
        download_pdf(pdf_url, filename)
    else:
        print(f"⚠️  No OA version for DOI: {doi}")
    time.sleep(1)  
