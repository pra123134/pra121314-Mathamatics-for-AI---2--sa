# interactive_injury_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Interactive Player Injury Dashboard", layout="wide")
sns.set(style="whitegrid")

st.title("⚽ Interactive Player Injury Impact Dashboard")

# ===================================
# 1. Data Upload / Dummy Data
# ===================================
uploaded_file = st.file_uploader("Upload CSV file (Player Injuries)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()
else:
    st.info("Using sample dummy data.")
    np.random.seed(42)
    players = [f"Player_{i}" for i in range(1, 21)]
    clubs = [f"Club_{i}" for i in range(1, 6)]
    dates = pd.date_range("2020-01-01", "2022-12-31", freq="15D")
    data = {
        "Player_Name": np.random.choice(players, 200),
        "Club_Name": np.random.choice(clubs, 200),
        "Rating": np.random.uniform(5, 9, 200),
        "Goals": np.random.randint(0, 5, 200),
        "Team_Goals_Before": np.random.randint(10, 30, 200),
        "Team_Goals_During": np.random.randint(5, 25, 200),
        "Age": np.random.randint(18, 35, 200),
        "Injury_Start": np.random.choice(dates, 200),
        "Injury_End": np.random.choice(dates, 200),
        "Status": np.random.choice(["Before", "During", "After"], 200)
    }
    df = pd.DataFrame(data)

# ===================================
# 2. Preprocessing
# ===================================
df['Rating'] = df['Rating'].fillna(df['Rating'].mean())
df['Goals'] = df['Goals'].fillna(0)
df['Injury_Start'] = pd.to_datetime(df['Injury_Start'], errors='coerce')
df['Injury_End'] = pd.to_datetime(df['Injury_End'], errors='coerce')
df['Avg_Rating_Before'] = df.groupby('Player_Name')['Rating'].shift(1).fillna(df['Rating'])
df['Avg_Rating_After'] = df.groupby('Player_Name')['Rating'].shift(-1).fillna(df['Rating'])
df['Team_Performance_Drop'] = df['Team_Goals_Before'] - df['Team_Goals_During']
df.rename(columns={'Player_Name': 'Player', 'Club_Name': 'Club'}, inplace=True)
df['Performance_Change'] = df['Avg_Rating_After'] - df['Avg_Rating_Before']
df['Month'] = df['Injury_Start'].dt.month

# ===================================
# 3. Sidebar Filters
# ===================================
st.sidebar.header("Filters")
players_filter = st.sidebar.multiselect("Select Player(s)", options=df['Player'].unique(), default=df['Player'].unique()[:5])
clubs_filter = st.sidebar.multiselect("Select Club(s)", options=df['Club'].unique(), default=df['Club'].unique())
status_filter = st.sidebar.multiselect("Select Status", options=df['Status'].unique(), default=df['Status'].unique())
date_range = st.sidebar.date_input("Injury Start Date Range", [df['Injury_Start'].min(), df['Injury_Start'].max()])
age_range = st.sidebar.slider("Player Age Range", int(df['Age'].min()), int(df['Age'].max()), (int(df['Age'].min()), int(df['Age'].max())))

filtered_df = df[
    (df['Player'].isin(players_filter)) &
    (df['Club'].isin(clubs_filter)) &
    (df['Status'].isin(status_filter)) &
    (df['Injury_Start'].dt.date >= date_range[0]) &
    (df['Injury_Start'].dt.date <= date_range[1]) &
    (df['Age'] >= age_range[0]) & (df['Age'] <= age_range[1])
]

# ===================================
# 4. Tabs for different visualizations
# ===================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Performance Drop",
    "📈 Timeline",
    "🗓 Injury Heatmap",
    "🎯 Age vs Drop",
    "🏆 Leaderboard"
])

# -----------------------------------
# Tab 1: Performance Drop Bar Chart
# -----------------------------------
with tab1:
    st.subheader("Top Injuries by Team Performance Drop")
    impact = filtered_df[['Player','Team_Performance_Drop']].sort_values('Team_Performance_Drop', ascending=False).head(10)
    fig = px.bar(impact, x='Team_Performance_Drop', y='Player', orientation='h', text='Team_Performance_Drop', color='Team_Performance_Drop',
                 color_continuous_scale='Reds', title="Top Injuries with Highest Team Performance Drop")
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Tab 2: Player Performance Timeline
# -----------------------------------
with tab2:
    st.subheader("Player Performance Timeline (Before & After Injury)")
    fig = go.Figure()
    for player in filtered_df['Player'].unique():
        player_data = filtered_df[filtered_df['Player']==player].sort_values('Injury_Start')
        fig.add_trace(go.Scatter(
            x=player_data['Injury_Start'],
            y=player_data['Rating'],
            mode='lines+markers',
            name=player,
            text=[f"Goals: {g}, Status: {s}" for g,s in zip(player_data['Goals'], player_data['Status'])]
        ))
    fig.update_layout(xaxis_title="Injury Start", yaxis_title="Rating", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Tab 3: Injury Frequency Heatmap
# -----------------------------------
with tab3:
    st.subheader("Injury Frequency by Month & Club")
    heatmap_data = filtered_df.groupby(['Club','Month']).size().unstack(fill_value=0)
    fig = px.imshow(heatmap_data, text_auto=True, color_continuous_scale='Blues', aspect="auto")
    fig.update_layout(xaxis_title="Month", yaxis_title="Club")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Tab 4: Age vs Team Performance Drop
# -----------------------------------
with tab4:
    st.subheader("Player Age vs Performance Drop")
    fig = px.scatter(filtered_df, x='Age', y='Team_Performance_Drop', color='Club', size='Goals', hover_data=['Player', 'Rating', 'Status'])
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Tab 5: Comeback Leaderboard
# -----------------------------------
with tab5:
    st.subheader("🏆 Comeback Players Leaderboard")
    leaderboard = filtered_df.groupby('Player')['Performance_Change'].mean().sort_values(ascending=False).head(10).reset_index()
    leaderboard['Performance_Change'] = leaderboard['Performance_Change'].round(2)
    st.dataframe(leaderboard)
