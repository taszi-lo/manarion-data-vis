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

    ACTIONTYPE_TO_ID = {
        "battle": '1',
        "fishing": '7',
        "woodcutting": '8',
        "mining": '9',
    }

    for p in playerdata:
        name = p['Name']
        for member_data in guilddata["Members"].values():
            if member_data.get("Name") == name:
                p["Potions"] = member_data.get("Potions", {})
                p["Rank"] = member_data.get("Rank")
                break
        actiontype = p.get("ActionType", "").lower()
        loot_id = ACTIONTYPE_TO_ID.get(actiontype)
        rank = str(p.get("Rank"))
        taxes = guilddata.get("Ranks", {}).get(rank, {}).get("taxes", {})
        p["TaxRate"] = taxes.get(loot_id, 0) if loot_id else 0
        
    path2 = Path('extended_playerdata.json')
    path2.write_text(json.dumps(playerdata, indent=4))