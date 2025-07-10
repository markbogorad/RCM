import re
import requests
import pandas as pd
from email_utils.serpapi_utils import google_search_results
from email_utils.usage_counter import increment_api_count, get_api_count, get_api_quota

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

def contextualweb_search_results(query, max_results=10):
    import os
    api_key = os.environ.get("CONTEXTUALWEB_API_KEY")
    if not api_key:
        try:
            from rcm_secrets import CONTEXTUALWEB_API_KEY
            api_key = CONTEXTUALWEB_API_KEY
        except ImportError:
            raise RuntimeError("ContextualWeb API key not found. Set CONTEXTUALWEB_API_KEY in rcm_secrets.py or as an environment variable.")
    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/WebSearchAPI"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }
    params = {
        "q": query,
        "pageNumber": 1,
        "pageSize": max_results,
        "autoCorrect": "true"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 429:
        # Quota exceeded
        return None, {"api": "contextualweb", "quota_exceeded": True, "count": get_api_count("contextualweb"), "quota": get_api_quota("contextualweb")}
    try:
        results = response.json()
        links = [item["url"] for item in results.get("value", [])]
        increment_api_count("contextualweb")
        # ContextualWeb does not provide quota info, so we can't show exact usage
        return [{"link": link} for link in links], {"api": "contextualweb", "quota_exceeded": False, "count": get_api_count("contextualweb"), "quota": get_api_quota("contextualweb")}
    except Exception as e:
        return None, {"api": "contextualweb", "quota_exceeded": False, "error": str(e), "count": get_api_count("contextualweb"), "quota": get_api_quota("contextualweb")}

def run_reverse_search(first, last, company, title=None, max_results=10, bulk=False):
    query_parts = [f'"{first} {last}"', company, title]
    filtered_parts = [str(part) for part in query_parts if part and not pd.isna(part)]
    query = " ".join(filtered_parts)
    if bulk:
        results, status = contextualweb_search_results(query, max_results=max_results)
        if results is not None:
            return results, status
        # Fallback to SerpAPI if ContextualWeb fails or quota is exceeded
        serp_results = google_search_results(query, max_results=max_results)
        increment_api_count("serpapi")
        # We can't get quota info from SerpAPI without an extra API call, so just note fallback
        return serp_results, {"api": "serpapi", "fallback": True, "count": get_api_count("serpapi"), "quota": get_api_quota("serpapi")}
    else:
        serp_results = google_search_results(query, max_results=max_results)
        increment_api_count("serpapi")
        return serp_results, {"api": "serpapi", "fallback": False, "count": get_api_count("serpapi"), "quota": get_api_quota("serpapi")}


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
