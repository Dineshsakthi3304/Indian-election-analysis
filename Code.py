import plotly.io as pio
pio.renderers.default = "browser"
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

# 1. Load your election dataset (ensure it’s in the same folder or provide full path)
df = pd.read_csv("indian-national-level-election.csv")

# --- Winning Margins Over Time (Interactive Scatter) ---
winners = df.loc[df.groupby(['year', 'pc_no'])['totvotpoll'].idxmax()]
runners_up = df.loc[df.groupby(['year', 'pc_no'])['totvotpoll'].apply(lambda x: x.nlargest(2).index[-1])]
winning_margins = winners[['year', 'pc_no', 'st_name', 'pc_name', 'partyname', 'totvotpoll']].merge(
    runners_up[['year', 'pc_no', 'totvotpoll']],
    on=['year', 'pc_no'],
    suffixes=('_winner', '_runnerup')
)
winning_margins['margin'] = winning_margins['totvotpoll_winner'] - winning_margins['totvotpoll_runnerup']

fig_margin = px.scatter(
    winning_margins, x='year', y='margin', color='partyname',
    hover_data=['st_name', 'pc_name'],
    title="Winning Margins Over the Years by Party",
    labels={'margin': 'Winning Margin (Votes)', 'partyname': 'Party'}
)

# --- Vote Share Trends for Top 5 Parties ---
top5 = df['partyname'].value_counts().nlargest(5).index
vote_share = df[df['partyname'].isin(top5)].groupby(['year', 'partyname'])['totvotpoll'].sum().reset_index()
vote_share['vote_share_pct'] = vote_share.groupby('year')['totvotpoll'].transform(lambda x: x / x.sum() * 100)

fig_vote = px.line(
    vote_share, x='year', y='vote_share_pct', color='partyname',
    markers=True,
    title="Vote Share % Over the Years (Top 5 Parties)",
    labels={'vote_share_pct': 'Vote Share (%)'}
)

# --- State-wise Dominant Party Map for Latest Year ---
latest_year = df['year'].max()
latest = df[df['year'] == latest_year]
latest_win = latest.loc[latest.groupby('pc_no')['totvotpoll'].idxmax()]

state_party = latest_win.groupby('st_name')['partyname'].agg(lambda x: x.value_counts().idxmax()).reset_index()

# Load GeoJSON boundaries of Indian states
with open(r"C:\Users\dinesh sakthi m\OneDrive\Desktop\Indian election analysis\in.json",encoding="utf-8") as f:
    india_geo = f.read()

# Ensure that 'st_name' in your data matches 'properties.ST_NM' in geojson.

fig_map = px.choropleth(
    state_party,
    geojson=india_geo,
    locations='st_name',
    featureidkey="properties.ST_NM",
    color='partyname',
    title=f"Dominant Party by State in {latest_year}",
    labels={'partyname': 'Party'}
)

fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

# --- Display all figures ---
fig_margin.show()
fig_vote.show()
fig_map.show()
