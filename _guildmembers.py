from pathlib import Path
import json
import requests

def _guildmembers():
    """Build the apis of the members and make a file from the data in them."""
    path = Path('guild_api_response.json')
    content = path.read_text(encoding="utf-8")
    data = json.loads(content)

    members = data['Members']

    players = []

    for member, info in members.items():
        players.append(info["Name"])

    playerapis = []

    for player in players:
        battlerapi = f"https://api.manarion.com/players/{player}"
        playerapis.append(battlerapi)

    playerdicts = []

    for link in playerapis:
        r = requests.get(link)
        response_dict = r.json()
        playerdicts.append(response_dict)

    playerstring = json.dumps(playerdicts, indent=4)
    path2 = Path('playerdata.json')
    path2.write_text(playerstring)
