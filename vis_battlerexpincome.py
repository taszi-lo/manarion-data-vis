from pathlib import Path
import json
import plotly.express as px
import math
from _guild_api import _guild_api
from _guildmembers import _guildmembers
from _api_merge import _api_merge

_guild_api(69, "GUILDAPI") # example _guild_api(30,"abcd-12345-6789")
_guildmembers()
_api_merge()

path = Path('extended_playerdata.json')
content = path.read_text(encoding='utf-8')
data = json.loads(content)

battlers, mob_strength, exp_boost, exp_codex, intellect = [], [], [], [], []

for member in data:
    if member["ActionType"] == "battle":
        battlers.append(member["Name"])
        mob_strength.append(member['Enemy'])
        exp_boost.append(member['TotalBoosts']['120']+(member['TotalBoosts']['108']+100)/100*member['Potions'].get('120',0)*5)
        exp_codex.append(member['TotalBoosts']['100'])
        intellect.append(1+(math.log((1+member['TotalBoosts']['3']/10000),10))/4)
exp_per_hit = []

for a, b, c, d in zip(mob_strength, exp_boost, exp_codex, intellect):
    result = (0.0002*(a+150)**2 + (a+150)**1.2 + 10*(a+150)) * (1+b/100) *(1+c/100) * d * 0.80
    exp_per_hit.append(result)

labels = {"x":"Battlers", "y": "Exp per hit"}
fig = px.bar(x=battlers, y=exp_per_hit, title="Exp income of the Divinity battlers", labels=labels )
fig.update_layout(xaxis={'categoryorder':'total ascending'})
fig.show()