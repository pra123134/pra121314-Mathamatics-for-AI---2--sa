import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set style
sns.set(style="whitegrid")

# ==========================
# Streamlit App Layout
# ==========================

st.title("⚽ Injury Impact & Player Performance Dashboard")

st.markdown("""
This interactive dashboard analyzes player injuries and their impact on team and individual performance.  
Upload your dataset (CSV) or try with a sample dataset.
""")

# ==========================
# File Upload
# ==========================

uploaded_file = st.file_uploader("📂 Upload your injury dataset (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    # Generate sample data
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
    st.info("Using a sample dataset (upload your own CSV for real analysis).")

# ==========================
# Step 2: Data Preprocessing
# ==========================

# ==========================
# Step 2: Data Preprocessing
# ==========================

required_cols = [
    "Player_Name", "Club_Name", "Rating", "Goals",
    "Team_Goals_Before", "Team_Goals_During",
    "Age", "Injury_Start", "Injury_End", "Status"
]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"❌ Missing columns in dataset: {missing_cols}")
    st.stop()

# Now safe to preprocess
df['Rating'] = df['Rating'].fillna(df['Rating'].mean())
df['Goals'] = df['Goals'].fillna(0)
df['Injury_Start'] = pd.to_datetime(df['Injury_Start'], errors='coerce')
df['Injury_End'] = pd.to_datetime(df['Injury_End'], errors='coerce')

df['Avg_Rating_Before'] = df.groupby('Player_Name')['Rating'].shift(1)
df['Avg_Rating_After'] = df.groupby('Player_Name')['Rating'].shift(-1)
df['Team_Performance_Drop'] = df['Team_Goals_Before'] - df['Team_Goals_During']

df.rename(columns={
    'Player_Name': 'Player',
    'Club_Name': 'Club'
}, inplace=True)

df['Performance_Change'] = df['Avg_Rating_After'] - df['Avg_Rating_Before']


# ==========================
# Step 3: EDA
# ==========================

summary = df.groupby('Player').agg({
    'Rating': 'mean',
    'Goals': 'sum',
    'Team_Performance_Drop': 'mean',
    'Injury_Start': 'count'
}).rename(columns={'Injury_Start': 'Injury_Count'}).reset_index()

impact = df[['Player', 'Team_Performance_Drop']].sort_values("Team_Performance_Drop", ascending=False).head(10)
leaderboard = df.groupby('Player')['Performance_Change'].mean().sort_values(ascending=False).head(10).reset_index()

# ==========================
# Step 4: Visualizations
# ==========================

st.header("📊 Visualizations")

# 1. Bar Chart
st.subheader("Top Injuries with Highest Team Performance Drop")
fig, ax = plt.subplots(figsize=(10,6))
sns.barplot(x='Team_Performance_Drop', y='Player', data=impact, palette="Reds_r", ax=ax)
st.pyplot(fig)

# 2. Line Chart
st.subheader("Player Performance Timeline (First 5 Players)")
fig, ax = plt.subplots(figsize=(12,6))
for player in df['Player'].unique()[:5]:
    player_data = df[df['Player'] == player].sort_values('Injury_Start')
    ax.plot(player_data['Injury_Start'], player_data['Rating'], label=player)
ax.legend()
st.pyplot(fig)

# 3. Heatmap
st.subheader("Injury Frequency by Month and Club")
df['Month'] = df['Injury_Start'].dt.month
heatmap_data = df.groupby(['Club','Month']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12,8))
sns.heatmap(heatmap_data, cmap="Blues", annot=True, fmt="d", ax=ax)
st.pyplot(fig)

# 4. Scatter Plot
st.subheader("Player Age vs. Performance Drop Index")
fig, ax = plt.subplots(figsize=(8,6))
sns.scatterplot(x=df['Age'], y=df['Team_Performance_Drop'], hue=df['Club'], ax=ax)
st.pyplot(fig)

# 5. Leaderboard
st.subheader("🏆 Comeback Players Leaderboard")
st.dataframe(leaderboard)

# ==========================
# End
# ==========================
st.success("Analysis complete ✅")
