import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import csv
import warnings
from bs4 import XMLParsedAsHTMLWarning

# Suppress XMLParsedAsHTMLWarning if needed
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

BASE_URL = "https://www.mosdac.gov.in"
VISITED = set()

# Directories
TEXT_DIR = "crawler"
FILE_DIR = os.path.join(TEXT_DIR, "downloads")
META_FILE = os.path.join(TEXT_DIR, "file_metadata.csv")
ALL_PAGES_FILE = os.path.join(TEXT_DIR, "all_pages.csv")

# Ensure output directories exist
os.makedirs(FILE_DIR, exist_ok=True)

# Exclude these patterns from crawling
EXCLUDE_PATTERNS = [
    "/feed", ".xml", "rss", "/internal/", "/logout", "/uops", "/taxonomy/term/"
]

def is_valid_link(url):
    return (
        url.startswith("http") and
        BASE_URL in url and
        not any(pattern in url for pattern in EXCLUDE_PATTERNS)
    )

def get_all_links(url):
    print(f"🔎 Scanning: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        links = set()
        for tag in soup.find_all('a', href=True):
            full_url = urljoin(BASE_URL, tag['href'])
            if is_valid_link(full_url):
                links.add(full_url)
        return links

    except Exception as e:
        print(f"⚠️ Error scanning {url}: {e}")
        return []

def crawl(start_url, depth=2):
    to_visit = set([start_url])
    all_links = set()

    for _ in range(depth):
        next_to_visit = set()
        for url in to_visit:
            if url not in VISITED:
                VISITED.add(url)
                found_links = get_all_links(url)
                all_links.update(found_links)
                next_to_visit.update(found_links)
        to_visit = next_to_visit

    return all_links

def save_links(links):
    with open(ALL_PAGES_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for link in sorted(links):
            writer.writerow([link])

if __name__ == "__main__":
    start_url = BASE_URL
    all_links = crawl(start_url, depth=2)
    print(f"\n✅ Total valid links found: {len(all_links)}")
    save_links(all_links)
