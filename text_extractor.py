
import pandas as pd
from pathlib import Path
import requests
import time
import fitz  # PyMuPDF
import os

# Config
INPUT_CSV = "DOI___Star_Ratings_for_UoA_20.csv"
OUTPUT_DIR = Path("uoa20_texts")
LOG_CSV = "uoa20_extraction_log.csv"
UNPAYWALL_EMAIL = "halabi@uel.ac.uk"  # Replace with your actual email

OUTPUT_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(INPUT_CSV)
log = []

def get_pdf_url_from_unpaywall(doi):
    print(f"🔍 Looking up Unpaywall for DOI: {doi}")
    api_url = f"https://api.unpaywall.org/v2/{doi}?email={UNPAYWALL_EMAIL}"
    response = requests.get(api_url, timeout=10)
    if response.status_code != 200:
        return None, f"Unpaywall error {response.status_code}"
    data = response.json()
    pdf_url = data.get("best_oa_location", {}).get("url_for_pdf")
    return pdf_url, None if pdf_url else "No OA PDF"

def download_pdf(pdf_url, filename):
    print(f"📥 Downloading PDF from: {pdf_url}")
    r = requests.get(pdf_url, stream=True, timeout=15)
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"✅ PDF saved as: {filename}")
        return True, None
    else:
        return False, f"Download failed: {r.status_code}"

def extract_text_from_pdf(pdf_path):
    print(f"📄 Extracting text from: {pdf_path}")
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

for idx, row in df.iterrows():
    doi = row['DOI']
    star = row['Assigned Star']
    safe_name = doi.replace('/', '_').replace(':', '_')
    out_path = OUTPUT_DIR / f"{safe_name}.txt"
    temp_pdf = f"temp_{safe_name}.pdf"

    print(f"\n[{idx+1}/{len(df)}] Processing: {doi}")

    if out_path.exists():
        print("⚠️ Already exists. Skipping.")
        log.append([doi, "✅ success", "", star])
        continue

    try:
        pdf_url, error = get_pdf_url_from_unpaywall(doi)
        if not pdf_url:
            print(f"❌ Failed to find PDF: {error}")
            log.append([doi, "❌ failed", error, star])
            continue

        success, reason = download_pdf(pdf_url, temp_pdf)
        if not success:
            print(f"❌ Download error: {reason}")
            log.append([doi, "❌ failed", reason, star])
            continue

        text = extract_text_from_pdf(temp_pdf)
        if not text.strip():
            print("❌ Extracted text is empty.")
            log.append([doi, "❌ failed", "Empty text", star])
        else:
            out_path.write_text(text, encoding='utf-8')
            print(f"💾 Text saved to: {out_path.name}")
            log.append([doi, "✅ success", "", star])

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        log.append([doi, "❌ failed", str(e), star])
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
        time.sleep(1)  # Rate limit

# Save log
log_df = pd.DataFrame(log, columns=["DOI", "Status", "Reason", "Assigned Star"])
log_df.to_csv(LOG_CSV, index=False)
print("\n✅ Extraction completed. See log for details.")
