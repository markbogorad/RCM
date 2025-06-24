# scraper_filter.py
import re
import requests
from bs4 import BeautifulSoup

def extract_contacts(html):
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
    return list(set(emails))

def score_relevance(html, keywords=None):
    if keywords is None:
        keywords = ['wealth management', 'research', 'insights', 'investment strategy', 'team']
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text().lower()
    score = sum(text.count(word.lower()) for word in keywords)
    return score
