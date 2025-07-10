import os
import json
from datetime import datetime

COUNTER_FILE = os.path.join(os.path.dirname(__file__), 'search_counter.json')
CONTEXTUALWEB_QUOTA = 10000
SERPAPI_QUOTA = 100  # adjust if you want to track this too


def _load_counter():
    if not os.path.exists(COUNTER_FILE):
        return {"contextualweb": {"count": 0, "last_reset": None}, "serpapi": {"count": 0, "last_reset": None}}
    with open(COUNTER_FILE, 'r') as f:
        return json.load(f)

def _save_counter(counter):
    with open(COUNTER_FILE, 'w') as f:
        json.dump(counter, f)

def _reset_if_needed(api):
    counter = _load_counter()
    now = datetime.now()
    this_month = now.strftime('%Y-%m')
    last_reset = counter[api].get("last_reset")
    if last_reset != this_month:
        counter[api]["count"] = 0
        counter[api]["last_reset"] = this_month
        _save_counter(counter)
    return counter

def increment_api_count(api):
    counter = _reset_if_needed(api)
    counter[api]["count"] += 1
    _save_counter(counter)
    return counter[api]["count"]

def get_api_count(api):
    counter = _reset_if_needed(api)
    return counter[api]["count"]

def get_api_quota(api):
    if api == "contextualweb":
        return CONTEXTUALWEB_QUOTA
    elif api == "serpapi":
        return SERPAPI_QUOTA
    return None 