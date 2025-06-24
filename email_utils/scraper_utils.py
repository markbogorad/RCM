import re
import requests
import pandas as pd
from email_utils.serpapi_utils import google_search_results

# Wide array of patterns, no domain attached
USERNAME_PATTERNS = [
    "{first}.{last}", "{first}_{last}", "{first}-{last}", "{first}{last}",
    "{f}{last}", "{first}", "{last}", "{last}{f}", "{l}{first}",
    "{f}.{last}", "{first}{l}", "{last}_{first}"
]

def generate_email_usernames(first, last):
    first, last = first.lower(), last.lower()
    f, l = first[0], last[0]
    return list(set(
        pattern.format(first=first, last=last, f=f, l=l)
        for pattern in USERNAME_PATTERNS
    ))

def run_reverse_search(first, last, company, title=None, max_results=10):
    query_parts = [f'"{first} {last}"', company, title]

    # Filter out anything that's None or NaN before joining
    filtered_parts = [str(part) for part in query_parts if part and not pd.isna(part)]

    query = " ".join(filtered_parts)
    return google_search_results(query, max_results=max_results)


def fetch_html_from_url(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.ok:
            return response.text
    except Exception as e:
        print(f"[!] Failed to fetch {url}: {e}")
    return ""

def extract_all_emails(html):
    EMAIL_REGEX = r"[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9.\-]+"
    return list(set(re.findall(EMAIL_REGEX, html)))

def extract_named_snippets(html, name, window=250):
    clean_text = re.sub(r'\s+', ' ', html)
    lower_text = clean_text.lower()
    name_lower = name.lower()

    matches = [m.start() for m in re.finditer(re.escape(name_lower), lower_text)]
    snippets = [clean_text[max(0, idx - window): idx + window] for idx in matches]

    return snippets or [clean_text[:1000]]  # fallback: first 1,000 chars if name not found

def match_username_to_name(username, first, last):
    username = username.lower()
    first, last = first.lower(), last.lower()
    f, l = first[0], last[0]

    # Strong exact-style matches
    if username in {
        f"{first}.{last}", f"{first}_{last}", f"{first}{last}",
        f"{f}{last}", f"{last}{f}", f"{last}.{first}"
    }:
        return True

    # Loose pattern matches
    if first in username and last in username:
        return True
    if username.startswith(f + last) or username.startswith(last + f):
        return True
    if username.startswith(first) and last[0] in username:
        return True
    if username.startswith(f) and last in username:
        return True
    if username.startswith(first[:3]) and last[:3] in username:
        return True

    return False
