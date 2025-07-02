import requests
from rcm_secrets import SERPAPI_KEY, MAX_RESULTS

def google_search_results(query, max_results=5):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        data = response.json()
        return data.get("organic_results", [])[:max_results]
    except Exception as e:
        print(f"SERPAPI failed: {e}")
        return []
