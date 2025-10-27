import requests
import json
from pathlib import Path

def _market_data():
    """ Make an api call, and store the response."""
    url= "https://api.manarion.com/market"
    r = requests.get(url)
    print(f"Status code: {r.status_code}")

    # Explore the structure of the data, write it to file.
    response_dict = r.json()
    response_string = json.dumps(response_dict, indent=4)
    path = Path('market_values.json')
    path.write_text(response_string)