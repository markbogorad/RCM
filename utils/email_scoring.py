# utils/email_scoring.py
import re
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import requests

model = SentenceTransformer('all-MiniLM-L6-v2')

REFERENCE_CONTEXTS = [
    "managing director of wealth management",
    "private client advisory services",
    "contact our institutional sales team",
    "financial advisor for private clients",
    "reach out to our investment advisor"
]
REFERENCE_EMBEDDINGS = model.encode(REFERENCE_CONTEXTS, convert_to_tensor=True)

def extract_emails_and_context(html, window=300):
    emails_with_context = []
    text = BeautifulSoup(html, "html.parser").get_text(separator=" ")
    matches = list(re.finditer(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
    for match in matches:
        start, end = match.span()
        context = text[max(0, start-window): min(len(text), end+window)]
        emails_with_context.append((match.group(), context))
    return emails_with_context

def score_email_contexts(email_contexts):
    results = []
    for email, context in email_contexts:
        context_embedding = model.encode(context, convert_to_tensor=True)
        similarity = util.cos_sim(context_embedding, REFERENCE_EMBEDDINGS).max().item()
        results.append((email, context, similarity))
    return sorted(results, key=lambda x: x[2], reverse=True)
