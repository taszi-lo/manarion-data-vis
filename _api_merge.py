from pathlib import Path
import json

def _api_merge():
    """Merge the potion info from guild api data to player api data."""
    guildpath = Path('guild_api_response.json')
    playerpath = Path('playerdata.json')

    guildcontent = guildpath.read_text()
    playercontent = playerpath.read_text()

    guilddata = json.loads(guildcontent)
    playerdata = json.loads(playercontent)

    for p in playerdata:
        name = p['Name']
        for member_id, member_data in guilddata["Members"].items():
            if member_data.get("Name") == name and "Potions" in member_data:
                p["Potions"] = member_data["Potions"]

    path2 = Path('extended_playerdata.json')
    path2.write_text(json.dumps(playerdata, indent=4))