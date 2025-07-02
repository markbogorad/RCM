import toml

with open("secrets.toml", "r") as f:
    secrets = toml.load(f)

MAPBOX_TOKEN = secrets["api_keys"]["mapbox"]
SERPAPI_KEY = secrets["api_keys"]["serpapi"]
MAX_RESULTS = secrets["api_keys"].get("max_results", 50)
