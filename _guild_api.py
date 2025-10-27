import requests
import json
from pathlib import Path

def _guild_api(guild_id, api_key):
    """ Make an api call, and store the response."""
    url= f"https://api.manarion.com/guilds/{guild_id}?apikey={api_key}"
    r = requests.get(url)
    print(f"Status code: {r.status_code}")

    # Checks if 200, write it to file.
    if r.status_code == 200:
        response_dict = r.json()
        response_string = json.dumps(response_dict, indent=4)
        path = Path('guild_api_response.json')
        path.write_text(response_string)
        print("JSON saved successfully.")
    else:
        print("Request failed - file not created.")