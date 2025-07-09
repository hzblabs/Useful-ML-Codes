
"""
Script: Combine full-text files with REF star ratings into a JSONL dataset.

Requirements:
- Each text file corresponds to a DOI (with special characters replaced)
- A CSV with columns: DOI, Assigned Star
- Text files are .txt and named like sanitized DOIs

Usage:
- Set your input paths below (csv_path, texts_folder, output_path)
"""

import os
import json
import pandas as pd

# --------------- USER INPUT ----------------
csv_path = ""          # CSV file with DOI and Assigned Star
texts_folder = ""          # Folder containing .txt files
output_path = ""  # Output file path
# -------------------------------------------

def sanitize_doi(doi):
    return doi.replace("/", "_").replace(":", "_")

def main():
    df = pd.read_csv(csv_path)
    records = []

    for _, row in df.iterrows():
        doi = row["DOI"]
        label = row["Assigned Star"]
        file_name = sanitize_doi(doi) + ".txt"
        file_path = os.path.join(texts_folder, file_name)

        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    records.append({
                        "text": text,
                        "label": str(label)
                    })
        else:
            print(f"⚠️ Missing file for DOI: {doi}")

    with open(output_path, "w", encoding="utf-8") as out_file:
        for record in records:
            json.dump(record, out_file)
            out_file.write("\n")

    print(f"✅ Saved {len(records)} records to {output_path}")

if __name__ == "__main__":
    main()
