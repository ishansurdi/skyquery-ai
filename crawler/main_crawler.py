import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode
import csv

# List of only selected URLs to crawl
target_urls = [
    "https://www.mosdac.gov.in",
    "https://www.mosdac.gov.in/tools",
    "https://www.mosdac.gov.in/3d-volumetric-terls-dwrproduct",
    "https://www.mosdac.gov.in/oceansat-3",
    "https://www.mosdac.gov.in/gps-derived-integrated-water-vapour",
    "https://www.mosdac.gov.in/soil-moisture-0",
    "https://www.mosdac.gov.in/river-discharge",
    "https://www.mosdac.gov.in/bayesian-based-mt-saphir-rainfall",
    "https://www.mosdac.gov.in/announcements",
    "https://www.mosdac.gov.in/gallery/index.html?&prod=3SIMG_%2A_L1B_STD_IR1_V%2A.jpg",
    "https://www.mosdac.gov.in/global-ocean-surface-current",
    "https://www.mosdac.gov.in/privacy-policy",
    "https://www.mosdac.gov.in/indian-mainland-coastal-product",
    "https://www.mosdac.gov.in/node?qt-services_quicktab=0#qt-services_quicktab",
    "https://www.mosdac.gov.in/node?qt-services_quicktab=3#qt-services_quicktab",
    "https://www.mosdac.gov.in/about-us",
    "https://www.mosdac.gov.in/",
    "https://www.mosdac.gov.in/hyperlink-policy",
    "https://www.mosdac.gov.in/validation-reports",
    "https://www.mosdac.gov.in/insat-3ds",
    "https://www.mosdac.gov.in/wave-based-renewable-energy",
    "https://www.mosdac.gov.in/insat-3d",
    "https://www.mosdac.gov.in/calibration-reports",
    "https://www.mosdac.gov.in/node?qt-services_quicktab=5#qt-services_quicktab",
    "https://www.mosdac.gov.in/data-access-policy",
    "https://www.mosdac.gov.in/insat-3a",
    "https://www.mosdac.gov.in/weather-reports",
    "https://www.mosdac.gov.in/sites/default/files/docs/Onset%20Prediction%202023.pdf",
    "https://www.mosdac.gov.in/sites/default/files/docs/INSAT_Product_Version_information_V01.pdf",
    "https://www.mosdac.gov.in/saral-altika",
    "https://www.mosdac.gov.in/node?qt-latest_products=4#qt-latest_products",
    "https://www.mosdac.gov.in/megha-tropiques",
    "https://www.mosdac.gov.in/atlases",
    "https://www.mosdac.gov.in/help",
    "https://www.mosdac.gov.in/sea-ice-occurrence-probability",
    "https://www.mosdac.gov.in/sitemap",
    "https://www.mosdac.gov.in/meteosat8-cloud-properties",
    "https://www.mosdac.gov.in/node?qt-services_quicktab=1#qt-services_quicktab",
    "https://www.mosdac.gov.in/copyright-policy",
    "https://www.mosdac.gov.in/inland-water-height",
    "https://www.mosdac.gov.in/data-quality",
    "https://www.mosdac.gov.in/faq-page",
    "https://www.mosdac.gov.in/kalpana-1",
    "https://www.mosdac.gov.in/node?qt-services_quicktab=2#qt-services_quicktab",
    "https://www.mosdac.gov.in/insat-3dr",
    "https://www.mosdac.gov.in/scatsat-1",
    "https://www.mosdac.gov.in/node?qt-latest_products=1#qt-latest_products",
    "https://www.mosdac.gov.in/node?qt-latest_products=2#qt-latest_products",
    "https://www.mosdac.gov.in/high-resolution-sea-surface-salinity",
    "https://www.mosdac.gov.in/mosdac-feedback",
    "https://www.mosdac.gov.in/website-policies",
    "https://www.mosdac.gov.in/node?qt-services_quicktab=4#qt-services_quicktab",
    "https://www.mosdac.gov.in/contact-us",
    "https://www.mosdac.gov.in/terms-conditions",
    "https://www.mosdac.gov.in/ocean-subsurface",
    "https://www.mosdac.gov.in/imageshow",
    "https://www.mosdac.gov.in/insitu",
    "https://www.mosdac.gov.in/oceansat-2",
    "https://www.mosdac.gov.in/node?qt-latest_products=3#qt-latest_products",
    "https://www.mosdac.gov.in/docs/STQC.pdf",
    "https://www.mosdac.gov.in/sites/default/files/docs/sftp-mosdac_0.pdf",
    "https://www.mosdac.gov.in/gallery/index.html%3F%26prod%3D3SIMG_%2A_L1B_STD_IR1_V%2A.jpg",
    "https://www.mosdac.gov.in/gsmap-isro-rain",
    "https://www.mosdac.gov.in/node?qt-latest_products=0#qt-latest_products",
    "https://www.mosdac.gov.in/sites/default/files/docs/Onset%20Prediction%202024.pdf",
    "https://www.mosdac.gov.in#main-content",
    "https://www.mosdac.gov.in/oceanic-eddies-detection"
]

BASE_DIR = r"C:\Users\Admin\Desktop\Restart\Hack\skyquery-ai\crawler"
FILE_DIR = os.path.join(BASE_DIR, "downloads")
META_FILE = os.path.join(BASE_DIR, "file_metadata.csv")
ALL_PAGES_FILE = os.path.join(BASE_DIR, "all_pages.txt")
FAILED_FILE_LOG = os.path.join(BASE_DIR, "failed_downloads.txt")

VISITED = set()
DOWNLOADED_FILES = set()

os.makedirs(FILE_DIR, exist_ok=True)

FILE_EXTENSIONS = ['.pdf', '.docx', '.xlsx', '.zip', '.jpg', '.png', '.jpeg', '.tif']
EXCLUDE_PATTERNS = ["/signup", "/auth/", "/sso/", "redirect_uri", "logout", "language=", "openid-connect"]

if not os.path.exists(META_FILE):
    with open(META_FILE, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "source_url", "file_type"])

def should_exclude(url):
    return any(pattern in url for pattern in EXCLUDE_PATTERNS)

def normalize_url(url):
    parsed = urlparse(url)
    clean_query = urlencode(sorted(parse_qsl(parsed.query)))
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', clean_query, ''))

def save_page_text(url, content):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator="\n", strip=True)
        clean = ''.join(c if c.isprintable() else ' ' for c in text)
        with open(ALL_PAGES_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "="*60 + "\n")
            f.write(f"🌐 URL: {url}\n")
            f.write("="*60 + "\n\n")
            f.write(clean + "\n")
        print(f"  📝 Saved text: {url}")
    except Exception as e:
        print(f"  ❌ Text parse fail: {url} - {e}")
        with open(FAILED_FILE_LOG, "a", encoding="utf-8") as logf:
            logf.write(f"TEXT_ERROR: {url} - {e}\n")

def save_file(url):
    try:
        filename = os.path.basename(urlparse(url).path)
        if not filename or filename in DOWNLOADED_FILES:
            return
        file_ext = os.path.splitext(filename)[1].lower()
        filepath = os.path.join(FILE_DIR, filename)
        print(f"  📥 Downloading: {filename}")
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        with open(META_FILE, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([filename, url, file_ext])
        DOWNLOADED_FILES.add(filename)
    except Exception as e:
        print(f"  ❌ File fail: {url} - {e}")
        with open(FAILED_FILE_LOG, "a", encoding="utf-8") as logf:
            logf.write(f"FILE_ERROR: {url} - {e}\n")

def crawl_page(url):
    url = normalize_url(url)
    if url in VISITED or should_exclude(url):
        return
    VISITED.add(url)
    try:
        print(f"\n🌐 Visiting: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            save_page_text(url, response.content)
            soup = BeautifulSoup(response.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = normalize_url(urljoin(url, href))
                if should_exclude(full_url):
                    continue
                if any(full_url.lower().endswith(ext) for ext in FILE_EXTENSIONS):
                    save_file(full_url)
        elif any(url.lower().endswith(ext) for ext in FILE_EXTENSIONS):
            save_file(url)
        else:
            print(f"  ⚠️ Skipping non-HTML: {url}")
    except Exception as e:
        print(f"  ⚠️ Page error: {url} - {e}")
        with open(FAILED_FILE_LOG, "a", encoding="utf-8") as logf:
            logf.write(f"PAGE_ERROR: {url} - {e}\n")

if __name__ == "__main__":
    print(f"🔍 Starting crawl of {len(target_urls)} URLs...")
    for url in target_urls:
        crawl_page(url)
    print("\n✅ Crawl completed!")
    print(f"📝 Text pages saved to: {ALL_PAGES_FILE}")
    print(f"📁 Files saved to: {FILE_DIR}")
    print(f"📄 Metadata saved to: {META_FILE}")
    print(f"⚠️ Failed downloads logged to: {FAILED_FILE_LOG}")
