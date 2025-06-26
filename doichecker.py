import os
import pandas as pd

# --- CONFIGURE ---
CSV_FILE = 'extracted_dois.csv'      # Your CSV file with DOIs or whatever you named it
PDF_FOLDER = 'ref_pdfs/'             # Folder containing the PDF files
OUTPUT_FILE = 'matched_dois.csv'     # Output CSV file
DOI_COLUMN = 'DOI'                   # Column name in your CSV

# --- STEP 1: Load DOIs from CSV ---
df = pd.read_csv(CSV_FILE)
doi_set = set(df[DOI_COLUMN].astype(str).str.strip())

# --- STEP 2: Extract DOI from PDF filenames and map them ---
matched = []
for fname in os.listdir(PDF_FOLDER):
    if fname.lower().endswith('.pdf'):
        name = os.path.splitext(fname)[0]  # Remove .pdf extension
        doi = name.replace("_", "/")       # Convert filename to DOI
        if doi in doi_set:
            matched.append({'DOI': doi, 'PDF_File': fname})

# --- STEP 3: Save matched DOIs with filenames to CSV ---
matched_df = pd.DataFrame(matched)
matched_df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Matched {len(matched)} DOIs saved to '{OUTPUT_FILE}'")
