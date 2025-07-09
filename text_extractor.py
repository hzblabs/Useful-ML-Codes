import pandas as pd
from pathlib import Path
import requests
import time
import fitz  # PyMuPDF
import os

# Config
INPUT_CSV = "DOI___Star_Ratings_for_UoA_4.csv"  
OUTPUT_DIR = Path("uoa4_texts")
LOG_CSV = "uoa4_extraction_log.csv"
UNPAYWALL_EMAIL = "halabi@uel.ac.uk"  
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
RETRY_LIMIT = 2

OUTPUT_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(INPUT_CSV)
log = []

def get_pdf_url_from_unpaywall(doi):
    print(f"🔍 Checking Unpaywall for DOI: {doi}")
    url = f"https://api.unpaywall.org/v2/{doi}?email={UNPAYWALL_EMAIL}"
    try:
        response = requests.get(url, timeout=15, headers=HEADERS)
        if response.status_code != 200:
            return None, f"Unpaywall error {response.status_code}"
        data = response.json()
        pdf_url = data.get("best_oa_location", {}).get("url_for_pdf")
        return pdf_url, None if pdf_url else "No OA PDF"
    except Exception as e:
        return None, f"Unpaywall exception: {e}"

def download_pdf(pdf_url, filename):
    for attempt in range(RETRY_LIMIT):
        try:
            r = requests.get(pdf_url, stream=True, timeout=20, headers=HEADERS)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(r.content)
                print(f"✅ PDF downloaded: {filename}")
                return True, None
            else:
                print(f"⚠️ Attempt {attempt+1} failed: {r.status_code}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} exception: {e}")
        time.sleep(2)
    return False, f"Download failed after {RETRY_LIMIT} attempts"

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return ""

for idx, row in df.iterrows():
    doi = row['DOI']
    star = row['Assigned Star']
    safe_name = doi.replace('/', '_').replace(':', '_')
    out_path = OUTPUT_DIR / f"{safe_name}.txt"
    temp_pdf = f"temp_{safe_name}.pdf"

    print(f"\n[{idx+1}/{len(df)}] Processing DOI: {doi}")

    if out_path.exists():
        print("⚠️ Already exists. Skipping.")
        log.append([doi, "✅ success", "", star])
        continue

    pdf_url, error = get_pdf_url_from_unpaywall(doi)
    if not pdf_url:
        print(f"❌ No PDF URL: {error}")
        log.append([doi, "❌ failed", error, star])
        continue

    success, reason = download_pdf(pdf_url, temp_pdf)
    if not success:
        print(f"❌ PDF download failed: {reason}")
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

    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)

    time.sleep(1)  # Respect API rate limits

# Save log
pd.DataFrame(log, columns=["DOI", "Status", "Reason", "Assigned Star"]).to_csv(LOG_CSV, index=False)
print("\n✅ Extraction process complete. See log for details.")
