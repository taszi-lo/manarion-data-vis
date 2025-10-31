import requests
import json
import time
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import math
from requests.exceptions import JSONDecodeError, RequestException

class ManaData():
    """A class for all the visualizations for Manarion."""
    def __init__(self, ID, API):
        """Initializing guild ID and api."""
        self.ID = ID
        self.API = API
        self.playerdata = []
        self.guilddata = None
        self.marketdata = None
        self._guild_api()
        self._guildmembers()
        self._api_merge()
        self._market_data()

    def _guild_api(self, max_retries=3, delay=1):
        """ Fetch guild data and write it toa file."""
        url= f"https://api.manarion.com/guilds/{self.ID}?apikey={self.API}"
        for attempt in range(1, max_retries+1):
            try:
                r = requests.get(url, timeout=10)
                print(f"Attempt {attempt}: status {r.status_code}")

                if r.status_code == 200:
                    try:
                        response_dict = r.json()
                        self.guilddata = response_dict
                        # writing to file if necessary: Path("guild_api_response.json").write_text(json.dumps(response_dict, indent=4)) 
                        print("Guild data saved successfully.")
                    except JSONDecodeError:
                        print("Received invalid JSON. Retrying..")
                else:
                    print(f"Bad status code: {r.status_code}. Retrying..")
            except RequestException as e:
                print(f"Request failed ({e}). Retrying..")

    def _guildmembers(self, max_retries=3, delay=1):
        """Fetch each member's data and write it to a file."""
        if not self.guilddata:
            raise ValueError("guilddata not loaded. Run _guild_api() first.")
        members = self.guilddata['Members']
        players = []
        for member_id, info in members.items():
            players.append(info["Name"])

        self.playerdata = []
        for player in players:
            url= f"https://api.manarion.com/players/{player}"

            for attempt in range(1, max_retries+1):
                try:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        try:
                            self.playerdata.append(r.json())
                            break
                        except JSONDecodeError:
                            print(f"Invalid JSON for {player}. Retrying..")
                    else:
                        print(f"Status {r.status_code} for {player}. Retrying..")
                except RequestException as e:
                    print(f"Error fetching {player}: {e}. Retrying..")
                time.sleep(delay)
            else:
                raise ConnectionError(f"All retries failed for player {player}.")
        
        # writing to file if necessary: Path("playerdata.json").write_text(json.dumps(self.playerdata, indent=4))
        

    def _market_data(self):
        """ Make an api call, and store the response."""
        url= "https://api.manarion.com/market"
        r = requests.get(url)
        print(f"Status code: {r.status_code}")

        # Explore the structure of the data, write it to file.
        if r.status_code == 200:
            self.marketdata = r.json()
            # writing to file if necessary: Path('market_values.json').write_text(json.dumps(self.marketdata, indent=4))
            print("Market data saved successfully.")
        else:
            print(f"Failed to fetch market data: {r.status_code}")
            return None

    def _api_merge(self):
        """Merge the potion and tax info from guild api data to player api data."""
        if not self.guilddata or not self.playerdata:
            raise ValueError("Missing data. Run _guild_api() and _guildmembers() first.")
        
        ACTIONTYPE_TO_ID = {
            "battle": '1',
            "fishing": '7',
            "woodcutting": '8',
            "mining": '9',
        }

        for p in self.playerdata:
            name = p['Name']
            for member_data in self.guilddata["Members"].values():
                if member_data.get("Name") == name:
                    p["Potions"] = member_data.get("Potions", {})
                    p["Rank"] = member_data.get("Rank")
                    break
            actiontype = p.get("ActionType", "").lower()
            loot_id = ACTIONTYPE_TO_ID.get(actiontype)
            rank = str(p.get("Rank"))
            taxes = self.guilddata.get("Ranks", {}).get(rank, {}).get("taxes", {})
            p["TaxRate"] = taxes.get(loot_id, 0) if loot_id else 0
            p["ExpTaxRate"] = taxes.get("42",0)
            
        # write to file if necessary: Path('extended_playerdata.json').write_text(json.dumps(self.playerdata, indent=4))

    def vis_battlerexpincome(self):
        """A visualization of the battlers' experience income per action."""
        guildname = self.guilddata['Name']

        battlers, mob_strength, exp_boost, exp_codex, intellect, exp_tax = [], [], [], [], [], []

        for member in self.playerdata:
            if member["ActionType"] == "battle":
                battlers.append(member["Name"])
                mob_strength.append(member['Enemy'])
                exp_boost.append(member['TotalBoosts']['120']+(member['TotalBoosts']['108']+100)/100*member['Potions'].get('120',0)*5)
                exp_codex.append(member['TotalBoosts']['100'])
                intellect.append(1+(math.log((1+member['TotalBoosts']['3']/10000),10))/4)
                exp_tax.append(member.get('ExpTaxRate',0))
        exp_per_hit = []

        for a, b, c, d,e in zip(mob_strength, exp_boost, exp_codex, intellect, exp_tax):
            result = (0.0002*(a+150)**2 + (a+150)**1.2 + 10*(a+150)) * (1+b/100) *(1+c/100) * d * (1-e/100) 
            exp_per_hit.append(result)

        labels = {"x":"Battlers", "y": "Exp per action"}
        fig = px.bar(x=battlers, y=exp_per_hit, title=f"Exp income of the {guildname} battlers", labels=labels )
        fig.update_layout(xaxis={'categoryorder':'total ascending'})
        fig.show()

    def vis_taxed_resources(self):
        """Visualizing the taxed resources of the gatherers of the guild.""" 

        guildname = self.guilddata['Name']
        members = self.guilddata['Members']

        filtered_members = []
        fish_7 = []
        wood_8 = []
        iron_9 = []

        for member, info in members.items():
            if info["ActionType"] != "battle":
                filtered_members.append(info["Name"])
                fish = info["Contributions"].get("7",0)
                wood = info["Contributions"].get("8",0)
                iron = info["Contributions"].get("9",0)
                fish_7.append(fish)
                wood_8.append(wood)
                iron_9.append(iron)

        title = f"Resource contribution of the {guildname} gatherers."

        fig = go.Figure()
        # One trace per contribution key.
        fig.add_trace(go.Bar(
            x=filtered_members,
            y=fish_7,
            name="Fish",
            marker_color="salmon",
        ))
        fig.add_trace(go.Bar(
            x=filtered_members,
            y=wood_8,
            name="Wood",
            marker_color="mediumseagreen",
        ))
        fig.add_trace(go.Bar(
            x=filtered_members,
            y=iron_9,
            name="Iron",
            marker_color="cornflowerblue",
        ))

        fig.update_layout(
            barmode="stack",
            title= title,
            template="plotly_white",
            xaxis_title ="Member",
            yaxis_title ="Total contribution",
        )
        fig.show()

    def vis_dustincome(self):
        """Visualization of the daily dust income of the guild members."""
        guildname = self.guilddata['Name']
        fishprice = (self.marketdata['Buy']['7']+self.marketdata['Sell']['7'])/2
        woodprice = (self.marketdata['Buy']['8']+self.marketdata['Sell']['8'])/2
        ironprice = (self.marketdata['Buy']['9']+self.marketdata['Sell']['9'])/2
        herbprice = ((self.marketdata['Buy']['40']+self.marketdata['Sell']['40'])/2 + (self.marketdata['Buy']['41']+self.marketdata['Sell']['41'])/2)/2

        players = []

        for member in self.playerdata:
            if member["ActionType"] == "battle":
                result = ((0.0001*(member['Enemy']+150)**2 + (member['Enemy']+150)**1.2 + 10*(member['Enemy']+150)) 
                        * (1.01**(((member['Enemy']+150)-150000)/2000)))*(1+member['TotalBoosts']['121']/100)*(1+member['TotalBoosts']['101']/100)*(1-member["TaxRate"]/100)*28800
                farm_production = 2.5 * ((1+member['BaseBoosts']['130']/100)**0.9 * (1+member['BaseBoosts']['131']/100)**0.9 * (1+member['BaseBoosts']['132']/100)**0.9)
                farm_upkeep = farm_production * 150000 * 24
                farm_income = farm_production * herbprice * 24-farm_upkeep
                potion_upkeep = ((((member["Potions"].get('122',0)*(member["Potions"].get('122',0)+1))+0.0002*member["Potions"].get('122',0)**3) + (member["Potions"].get('120',0)*(member['Potions'].get('120',0)+1)/2+0.0002*member["Potions"].get("120",0)**3))*herbprice)*24/(1+member['TotalBoosts']['110']/100)
                players.append({
                    "name": member["Name"],
                    "income": result,
                    "herbincome": farm_income - potion_upkeep,
                    "actiontype": member['ActionType']
                })
            elif member["ActionType"] == "mining":
                result1 = member['TotalBoosts']['30']*(member['TotalBoosts']['124']/100 + (member['Potions'].get('124',0)/10)*(1+member['TotalBoosts']['108']/100)+member["MiningLevel"]*0.03)*(1+member['TotalBoosts']['106']/100)*(1-member["TaxRate"]/100)*28800
                farm_production = 2.5 * ((1+member['BaseBoosts']['130']/100)**0.9 * (1+member['BaseBoosts']['131']/100)**0.9 * (1+member['BaseBoosts']['132']/100)**0.9)
                farm_upkeep = farm_production * 150000 * 24
                farm_income = farm_production * herbprice * 24-farm_upkeep
                potion_upkeep = ((((member["Potions"].get('122',0)*(member["Potions"].get('122',0)+1))+0.0002*member["Potions"].get('122',0)**3) + (member["Potions"].get('124',0)*(member['Potions'].get('124',0)+1)/2+0.0002*member["Potions"].get("124",0)**3))*herbprice)*24/(1+member['TotalBoosts']['110']/100)
                players.append({
                    "name": member["Name"],
                    "income": result1 * ironprice,
                    "herbincome": farm_income - potion_upkeep,
                    "actiontype": member['ActionType']
                })
            elif member["ActionType"] == "fishing":
                result2 = member['TotalBoosts']['31']*(member['TotalBoosts']['124']/100 + (member['Potions'].get('124',0)/10)*(1+member['TotalBoosts']['108']/100)+member["FishingLevel"]*0.03)*(1+member['TotalBoosts']['106']/100)*(1-member["TaxRate"]/100)*28800
                farm_production = 2.5 * ((1+member['BaseBoosts']['130']/100)**0.9 * (1+member['BaseBoosts']['131']/100)**0.9 * (1+member['BaseBoosts']['132']/100)**0.9)
                farm_upkeep = farm_production * 150000 * 24
                farm_income = farm_production * herbprice * 24-farm_upkeep
                potion_upkeep = ((((member["Potions"].get('122',0)*(member["Potions"].get('122',0)+1))+0.0002*member["Potions"].get('122',0)**3) + (member["Potions"].get('124',0)*(member['Potions'].get('124',0)+1)/2+0.0002*member["Potions"].get("124",0)**3))*herbprice)*24/(1+member['TotalBoosts']['110']/100)
                players.append({
                    "name": member["Name"],
                    "income": result2 * fishprice,
                    "herbincome": farm_income - potion_upkeep,
                    "actiontype": member['ActionType']
                })
            elif member["ActionType"] == "woodcutting":
                result3 = member['TotalBoosts']['32']*(member['TotalBoosts']['124']/100 + (member['Potions'].get('124',0)/10)*(1+member['TotalBoosts']['108']/100)+member["WoodcuttingLevel"]*0.03)*(1+member['TotalBoosts']['106']/100)*(1-member["TaxRate"]/100)*28800
                farm_production = 2.5 * ((1+member['BaseBoosts']['130']/100)**0.9 * (1+member['BaseBoosts']['131']/100)**0.9 * (1+member['BaseBoosts']['132']/100)**0.9)
                farm_upkeep = farm_production * 150000 * 24
                farm_income = farm_production * herbprice * 24-farm_upkeep
                potion_upkeep = ((((member["Potions"].get('122',0)*(member["Potions"].get('122',0)+1))+0.0002*member["Potions"].get('122',0)**3) + (member["Potions"].get('124',0)*(member['Potions'].get('124',0)+1)/2+0.0002*member["Potions"].get("124",0)**3))*herbprice)*24/(1+member['TotalBoosts']['110']/100)
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
            title=f"Dust income of the {guildname} members",
            xaxis_title="Members",
            yaxis_title="Daily income in dust",
            xaxis=dict(categoryorder='array', categoryarray=sorted_names)
        )

        fig.show()