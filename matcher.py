import os
import pandas as pd

# Load DOI list
df = pd.read_csv("newdoi.csv")  # or read_excel if xlsx
doi_list = df['DOI'].dropna().unique()
normalized_dois = {doi.replace("/", "_").lower(): doi for doi in doi_list}

pdf_folder = "newref_pdfs"
matches = []
unmatched = []

for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        file_key = filename.replace(".pdf", "").lower()
        matched = False
        for doi_key, original_doi in normalized_dois.items():
            if doi_key in file_key:
                matches.append({"filename": filename, "matched_doi": original_doi})
                matched = True
                break
        if not matched:
            unmatched.append(filename)

# Save matched
pd.DataFrame(matches).to_csv("matched_dois.csv", index=False)

# Save unmatched
pd.DataFrame(unmatched, columns=["unmatched_filename"]).to_csv("unmatched_pdfs.csv", index=False)

print("Done: matched_dois.csv and unmatched_pdfs.csv generated.")
