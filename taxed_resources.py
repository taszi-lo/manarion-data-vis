from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import json

path = Path('guild_api_response.json')
content = path.read_text(encoding="utf-8")
data = json.loads(content)

members = data['Members']

filtered_members = []
fish_7 = []
wood_8 = []
iron_9 = []

for member_id, info in members.items():
    if info["ActionType"] != "battle":
        filtered_members.append(info["Name"])
        fish = info["Contributions"].get("7",0)
        wood = info["Contributions"].get("8",0)
        iron = info["Contributions"].get("9",0)
        fish_7.append(fish)
        wood_8.append(wood)
        iron_9.append(iron)

title = "Guild resource contributions"
labels = {"x": "Gatherers", "y": "Total Resource Contributions"}
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



"""names = []
codex = []
for member_id, info in members.items():
    name = info["Name"]
    names.append(name)
    codi = info["Contributions"].get("3", 0)
    codex.append(codi)

title = "Guild contributions"
labels = {"x": "Members", "y": "Contributions"}
fig = px.bar(x=names, y=codex, title=title, labels=labels)
fig.show()"""