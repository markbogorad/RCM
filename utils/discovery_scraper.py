# discovery_scraper.py
import requests
from bs4 import BeautifulSoup
from utils.serpapi_utils import get_urls_from_query
from utils.semantic_utils import semantic_score

def get_clean_text(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return ""

def score_urls_from_query(query: str):
    urls = get_urls_from_query(query)
    scored = []
    for url in urls:
        text = get_clean_text(url)
        if len(text) > 300:
            score = semantic_score(text)
            scored.append((url, score))
    return sorted(scored, key=lambda x: x[1], reverse=True)
