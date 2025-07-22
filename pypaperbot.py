import os, csv, time, requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException

# -------- CONFIG --------
DOI_FILE = "doi.txt"   # Change to the name of your doi file
OUTPUT_DIR = "./pdfs"
LOG_FILE = "scihub_log.csv"
MIRRORS = [
    "https://sci-hub.in",
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.hkvisa.net"
]
PDF_MIN_SIZE = 10000  # in bytes

# -------- SETUP --------
os.makedirs(OUTPUT_DIR, exist_ok=True)

def start_browser():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    return uc.Chrome(options=options)

def extract_pdf_url(driver, doi, mirror):
    try:
        url = f"{mirror.rstrip('/')}/{quote_plus(doi)}"
        driver.get(url)
        time.sleep(5)  # Allow JS to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        src = None

        # 1. Check iframe
        iframe = soup.find("iframe")
        if iframe and "src" in iframe.attrs:
            src = iframe["src"]

        # 2. Fallback: embed/object/a
        if not src:
            embed = soup.find("embed")
            if embed and "src" in embed.attrs:
                src = embed["src"]

        if not src:
            obj = soup.find("object")
            if obj and "data" in obj.attrs:
                src = obj["data"]

        if not src:
            link = soup.find("a", href=lambda x: x and x.endswith(".pdf"))
            if link:
                src = link["href"]

        if not src:
            return None

        src = src.strip()
        if src.startswith("//"):
            return "https:" + src
        elif src.startswith("/"):
            return mirror.rstrip("/") + src
        elif src.startswith("http"):
            return src
        else:
            return mirror.rstrip("/") + "/" + src
    except TimeoutException:
        return None

def download_pdf(pdf_url, output_path):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(pdf_url, headers=headers, stream=True, timeout=30)
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))

        if r.status_code == 200 and "application/pdf" in content_type and content_length > PDF_MIN_SIZE:
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"⚠️ Not a valid PDF – Type: {content_type}, Size: {content_length}")
    except Exception as e:
        print(f"❌ Exception during download: {e}")
    return False

# -------- MAIN --------
with open(DOI_FILE, "r") as f:
    dois = [line.strip() for line in f if line.strip()]

driver = start_browser()
results = []

for i, doi in enumerate(dois, 1):
    print(f"[{i}/{len(dois)}] DOI: {doi}")
    filename = doi.replace("/", "_") + ".pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(output_path):
        print(f"✅ Already exists: {filename}")
        results.append([doi, "SKIPPED", "Already downloaded", ""])
        continue

    success = False
    for mirror in MIRRORS:
        print(f"🌐 Trying mirror: {mirror}")
        pdf_url = extract_pdf_url(driver, doi, mirror)

        if pdf_url:
            print(f"🔗 PDF link: {pdf_url}")
            if download_pdf(pdf_url, output_path):
                print(f"✅ Saved: {filename}")
                results.append([doi, "DOWNLOADED", mirror, pdf_url])
                success = True
                break
            else:
                print(f"❌ Failed to download from: {mirror}")
        else:
            print(f"❌ No PDF found on: {mirror}")
        time.sleep(1)

    if not success:
        results.append([doi, "FAILED", "None", "N/A"])
        print(f"❌ Failed: {doi}")

    time.sleep(2)

driver.quit()

# -------- LOG SAVE --------
with open(LOG_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["DOI", "Status", "Mirror", "PDF URL"])
    writer.writerows(results)

print(f"\n✅ All done. Log saved to {LOG_FILE}")
