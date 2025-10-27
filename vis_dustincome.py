from pathlib import Path
import json
import plotly.express as px
import plotly.graph_objects as go
from _guild_api import _guild_api
from _guildmembers import _guildmembers
from _api_merge import _api_merge
from _market_data import _market_data

_guild_api(GUILDID,"GUILDAPI") # example _guild_api(30,"abcd-12345-6789")
_market_data()
_guildmembers()
_api_merge()

playerpath = Path('extended_playerdata.json')
marketpath = Path('market_values.json')
playercontent = playerpath.read_text(encoding='utf-8')
marketcontent = marketpath.read_text(encoding='utf-8')
playerdata = json.loads(playercontent)
marketdata = json.loads(marketcontent)

ironprice = (marketdata['Buy']['7']+marketdata['Sell']['7'])/2
fishprice = (marketdata['Buy']['8']+marketdata['Sell']['8'])/2
woodprice = (marketdata['Buy']['9']+marketdata['Sell']['9'])/2
herbprice = ((marketdata['Buy']['40']+marketdata['Sell']['40'])/2 + (marketdata['Buy']['41']+marketdata['Sell']['41'])/2)/2

players = []

for member in playerdata:
    if member["ActionType"] == "battle":
        result = ((0.0001*(member['Enemy']+150)**2 + (member['Enemy']+150)**1.2 + 10*(member['Enemy']+150)) 
                  * (1.01**(((member['Enemy']+150)-150000)/2000)))*(1+member['TotalBoosts']['121']/100)*(1+member['TotalBoosts']['101']/100)*0.75*28800
        farm_production = 2.5 * ((1+member['BaseBoosts']['130']/100)**0.9 * (1+member['BaseBoosts']['131']/100)**0.9 * (1+member['BaseBoosts']['132']/100)**0.9)
        farm_upkeep = farm_production * 150000 * 24
        farm_income = farm_production * herbprice * 24-farm_upkeep
        potion_upkeep = ((((member["Potions"].get('122',0)*(member["Potions"].get('122',0)+1))+0.0002*member["Potions"].get('122',0)**3) + (member["Potions"].get('120',0)*(member['Potions'].get('120',0)+1)/2+0.0002*member["Potions"]["120"]**3))*herbprice)*24/(1+member['TotalBoosts']['110']/100)
        players.append({
            "name": member["Name"],
            "income": result,
            "herbincome": farm_income - potion_upkeep,
            "actiontype": member['ActionType']
        })
    elif member["ActionType"] == "mining":
        result1 = member['TotalBoosts']['30']*(member['TotalBoosts']['124']/100 + (member['Potions']['124']/10)*(1+member['TotalBoosts']['108']/100)+member["MiningLevel"]*0.03)*(1+member['TotalBoosts']['106']/100)*0.6*28800
        farm_production = 2.5 * ((1+member['BaseBoosts']['130']/100)**0.9 * (1+member['BaseBoosts']['131']/100)**0.9 * (1+member['BaseBoosts']['132']/100)**0.9)
        farm_upkeep = farm_production * 150000 * 24
        farm_income = farm_production * herbprice * 24-farm_upkeep
        potion_upkeep = ((((member["Potions"].get('122',0)*(member["Potions"].get('122',0)+1))+0.0002*member["Potions"].get('122',0)**3) + (member["Potions"].get('124',0)*(member['Potions'].get('124',0)+1)/2+0.0002*member["Potions"]["124"]**3))*herbprice)*24/(1+member['TotalBoosts']['110']/100)
        players.append({
            "name": member["Name"],
            "income": result1 * ironprice,
            "herbincome": farm_income - potion_upkeep,
            "actiontype": member['ActionType']
        })
    elif member["ActionType"] == "fishing":
        result2 = member['TotalBoosts']['31']*(member['TotalBoosts']['124']/100 + (member['Potions']['124']/10)*(1+member['TotalBoosts']['108']/100)+member["FishingLevel"]*0.03)*(1+member['TotalBoosts']['106']/100)*0.6*28800
        farm_production = 2.5 * ((1+member['BaseBoosts']['130']/100)**0.9 * (1+member['BaseBoosts']['131']/100)**0.9 * (1+member['BaseBoosts']['132']/100)**0.9)
        farm_upkeep = farm_production * 150000 * 24
        farm_income = farm_production * herbprice * 24-farm_upkeep
        potion_upkeep = ((((member["Potions"].get('122',0)*(member["Potions"].get('122',0)+1))+0.0002*member["Potions"].get('122',0)**3) + (member["Potions"].get('124',0)*(member['Potions'].get('124',0)+1)/2+0.0002*member["Potions"]["124"]**3))*herbprice)*24/(1+member['TotalBoosts']['110']/100)
        players.append({
            "name": member["Name"],
            "income": result2 * fishprice,
            "herbincome": farm_income - potion_upkeep,
            "actiontype": member['ActionType']
        })
    elif member["ActionType"] == "woodcutting":
        result3 = member['TotalBoosts']['32']*(member['TotalBoosts']['124']/100 + (member['Potions']['124']/10)*(1+member['TotalBoosts']['108']/100)+member["WoodcuttingLevel"]*0.03)*(1+member['TotalBoosts']['106']/100)*0.6*28800
        farm_production = 2.5 * ((1+member['BaseBoosts']['130']/100)**0.9 * (1+member['BaseBoosts']['131']/100)**0.9 * (1+member['BaseBoosts']['132']/100)**0.9)
        farm_upkeep = farm_production * 150000 * 24
        farm_income = farm_production * herbprice * 24-farm_upkeep
        potion_upkeep = ((((member["Potions"].get('122',0)*(member["Potions"].get('122',0)+1))+0.0002*member["Potions"].get('122',0)**3) + (member["Potions"].get('124',0)*(member['Potions'].get('124',0)+1)/2+0.0002*member["Potions"]["124"]**3))*herbprice)*24/(1+member['TotalBoosts']['110']/100)
        players.append({
            "name": member["Name"],
            "income": result3 * woodprice,
            "herbincome": farm_income - potion_upkeep,
            "actiontype": member['ActionType']
        })

data = []
order_helper = []

for p in players:
    herb_value = p.get("herbincome", 0)
    income_value = p.get("income", 0)
    total_w_neg_herb = income_value + herb_value
    order_helper.append({"name": p['name'], "net": total_w_neg_herb})
    
    if herb_value >= 0:
        # Positive herb: stack normally
        data.append({"name": p["name"], "type": "Income", "income": income_value, "display_colour": p["actiontype"]})
        data.append({"name": p["name"], "type": "FarmProfit", "income": herb_value, "display_colour": "FarmProfit"})
    elif total_w_neg_herb >= 0:
        # Negative herb but positive total: show income bar up to total, then FarmLoss extending from total to income_value
        data.append({"name": p["name"], "type": "Income", "income": total_w_neg_herb, "display_colour": p["actiontype"]})
        data.append({"name": p["name"], "type": "FarmLoss", "income": abs(herb_value), "display_colour": "FarmLoss"})
    else:
        # Both negative: show only negative striped bar
        data.append({"name": p["name"], "type": "FarmLoss", "income": total_w_neg_herb, "display_colour": "FarmLoss"})

sorted_names = [x["name"] for x in sorted(order_helper, key=lambda x: x["net"], reverse=False)]

colour_map = {
    "battle": "#dd2200",
    "mining": "#333333",
    "fishing": "#3030cc",
    "woodcutting": "#20dd20",
    "FarmProfit": "#eeeeee",
    "FarmLoss": "#999999"
}

# Create separate traces for each display_colour in the order you want them stacked
fig = go.Figure()

# Add traces in bottom-to-top order
for display_colour in ["battle", "mining", "fishing", "woodcutting", "FarmProfit", "FarmLoss"]:
    filtered_data = [d for d in data if d["display_colour"] == display_colour]
    if filtered_data:
        names = [d["name"] for d in filtered_data]
        incomes = [d["income"] for d in filtered_data]
        
        pattern = dict(shape="/", fgcolor="rgba(0,0,0,0.35)") if display_colour == "FarmLoss" else None
        
        fig.add_trace(go.Bar(
            name=display_colour,
            x=names,
            y=incomes,
            marker=dict(
                color=colour_map[display_colour],
                line=dict(color="black", width=1),
                pattern=pattern
            )
        ))

fig.update_layout(
    barmode='stack',
    title="Dust income of the Divinity members",
    xaxis_title="Members",
    yaxis_title="Daily income in dust",
    xaxis=dict(categoryorder='array', categoryarray=sorted_names)
)

fig.show()