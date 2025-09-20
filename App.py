# interactive_player_injury_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------
# Sample Synthetic Data (replace with your CSV)
# ------------------------
np.random.seed(42)
players = [f"Player_{i}" for i in range(1, 21)]
clubs = [f"Club_{i}" for i in range(1, 6)]
dates = pd.date_range("2025-01-01", "2025-09-20", freq="7D")

rows = 200
data = pd.DataFrame({
    "Player": np.random.choice(players, rows),
    "Club": np.random.choice(clubs, rows),
    "Rating": np.random.uniform(5, 9, rows),
    "Goals": np.random.randint(0, 5, rows),
    "Team_Goals_Before": np.random.randint(10, 30, rows),
    "Team_Goals_During": np.random.randint(5, 25, rows),
    "Age": np.random.randint(18, 35, rows),
    "Injury_Start": np.random.choice(dates, rows),
    "Injury_End": np.random.choice(dates, rows),
    "Status": np.random.choice(["Before", "During", "After"], rows)
})

# Preprocessing
data['Avg_Rating_Before'] = data.groupby('Player')['Rating'].shift(1).fillna(data['Rating'])
data['Avg_Rating_After'] = data.groupby('Player')['Rating'].shift(-1).fillna(data['Rating'])
data['Team_Performance_Drop'] = data['Team_Goals_Before'] - data['Team_Goals_During']
data['Performance_Change'] = data['Avg_Rating_After'] - data['Avg_Rating_Before']
data['Month'] = data['Injury_Start'].dt.month

# ------------------------
# Streamlit UI
# ------------------------
st.set_page_config(page_title="Player Injury Dashboard", layout="wide")
st.title("⚽ Interactive Player Injury Dashboard")

# Last update
import datetime
last_update = datetime.date.today() - datetime.timedelta(days=1)
st.markdown(f"**Last update:** {last_update.strftime('%Y-%m-%d')}")

st.sidebar.header("🔍 Apply Filters")

# Multi-select filters
player_filter = st.sidebar.multiselect("Player", options=data['Player'].unique(), default=[])
club_filter = st.sidebar.multiselect("Club", options=data['Club'].unique(), default=[])
status_filter = st.sidebar.multiselect("Status", options=data['Status'].unique(), default=[])
month_filter = st.sidebar.multiselect("Month", options=sorted(data['Month'].unique()), default=[])

# ------------------------
# Filtering logic
# ------------------------
filtered_data = data.copy()
if player_filter:
    filtered_data = filtered_data[filtered_data['Player'].isin(player_filter)]
if club_filter:
    filtered_data = filtered_data[filtered_data['Club'].isin(club_filter)]
if status_filter:
    filtered_data = filtered_data[filtered_data['Status'].isin(status_filter)]
if month_filter:
    filtered_data = filtered_data[filtered_data['Month'].isin(month_filter)]

# ------------------------
# Dynamic Graphs
# ------------------------
if filtered_data.empty:
    st.warning("⚠️ No data available for the selected filters. Try adjusting your selections.")
else:
    st.subheader("📈 Player Performance Trends")
    
    # Overall line chart
    fig = px.line(filtered_data, x="Injury_Start", y="Rating", color="Player",
                  title="Player Ratings Over Time", markers=True, hover_data=["Goals","Status"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔎 Breakdown by Selected Filters")
    grouping_columns = []
    if player_filter: grouping_columns.append("Player")
    if club_filter: grouping_columns.append("Club")
    if status_filter: grouping_columns.append("Status")
    if month_filter: grouping_columns.append("Month")

    if grouping_columns:
        grouped = filtered_data.groupby(grouping_columns + ["Injury_Start"], as_index=False).agg({"Rating":"mean"})
        for group_vals, df_subset in grouped.groupby(grouping_columns):
            group_title = ", ".join([f"{col}: {val}" for col, val in zip(grouping_columns, group_vals if isinstance(group_vals, tuple) else [group_vals])])
            fig = px.line(df_subset, x="Injury_Start", y="Rating", markers=True, title=f"Trend for {group_title}")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ Select one or more filters to see condition-specific trends.")
