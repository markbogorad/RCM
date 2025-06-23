import re
from bs4 import BeautifulSoup
from utils.semantic_utils import semantic_score

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def extract_emails_and_context(html, window=250):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    matches = list(re.finditer(EMAIL_REGEX, text))
    
    results = []
    for match in matches:
        start = max(0, match.start() - window)
        end = match.end() + window
        context = text[start:end]
        results.append((match.group(), context))
    return results

def score_email_contexts(email_context_pairs):
    results = []
    for email, context in email_context_pairs:
        try:
            score = semantic_score(context)
            results.append((email, context, score))
        except Exception:
            continue
    return sorted(results, key=lambda x: x[2], reverse=True)
