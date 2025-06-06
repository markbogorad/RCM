import requests
from utils.config import SERPAPI_KEY, MAX_RESULTS

def get_urls_from_query(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        data = response.json()
        return [res["link"] for res in data.get("organic_results", [])][:MAX_RESULTS]
    except Exception as e:
        print(f"SERPAPI failed: {e}")
        return []
