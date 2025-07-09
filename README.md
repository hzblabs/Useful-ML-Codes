# 📄 REF Paper PDF Downloader and other useful tools

This Python script helps you automatically download **open access PDFs** for a list of DOIs using the [Unpaywall API](https://unpaywall.org/products/api). It's particularly useful for research projects like the **Research Excellence Framework (REF)** where you need full-text academic outputs.

## 🚀 Features

- Fetches OA PDF URLs via the Unpaywall API
- Downloads PDFs and saves them locally
- Handles errors gracefully
- Avoids duplicate downloads
- Rate-limited to respect API policies
- Matches pdf to DOIS
- Merge json files together
- Clean json files
- Count number of samples in json file
- Extarct text from pdfs and keep track of status either success or failed

## 🛠️ Requirements

- Python 3.x
- `requests`, `pandas`
  Install dependencies:

  ```
  pip install requests pandas
  ```

## 📂 Project Structure

```
.
├── extracted_dois.csv     # Your input CSV with a 'DOI' column
├── ref_pdfs/              # Downloaded PDFs will be saved here
└── download_ref_pdfs.py   # Main script
```

---

## 📋 Setup

1. **Insert your email** in the script (Unpaywall requires it):

   ```python
   EMAIL = "your_email@example.com"
   ```

2. **Prepare your CSV** file named `extracted_dois.csv` with a column titled `DOI`.

3. **Run the script**:

   ```
   python download_ref_pdfs.py
   ```

---

## 📌 Notes

- The script uses `doi.replace("/", "_")` to ensure valid filenames.
- A 1-second delay between requests helps you stay compliant with API usage limits.
- Only works for **open access** papers.

---

## 🧠 Attribution

This script uses the [Unpaywall API](https://unpaywall.org/products/api), which provides free access to millions of open-access research papers.

---

## 📧 Contact

Created by Hazeeb – feel free to reach out for questions or improvements!
