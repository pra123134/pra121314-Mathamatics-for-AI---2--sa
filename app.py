import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import traceback

# Set Streamlit page config
st.set_page_config(page_title="Injury Data Analysis", layout="wide")

st.title("⚽ Injury Data Analysis Dashboard")
st.markdown("Upload your dataset or use the demo dataset to explore injuries, performance drops, and player comebacks.")

# =====================================
# File Upload or Demo Data
# =====================================
try:
    uploaded_file = st.file_uploader("📂 Upload your CSV dataset", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Dataset uploaded successfully!")
    else:
        # Create demo data if no file uploaded
        st.warning("⚠ No dataset uploaded. Using demo dataset instead.")
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

    # =====================================
    # Preprocessing
    # =====================================
    st.subheader("🔧 Data Preprocessing")

    try:
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

        st.write("✅ Data preprocessing completed!")
        st.write(df.head())

    except Exception as e:
        st.error("❌ Error during preprocessing!")
        st.exception(e)
        st.stop()

    # =====================================
    # Exploratory Data Analysis
    # =====================================
    st.subheader("📊 Exploratory Data Analysis")

    try:
        summary = df.groupby('Player').agg({
            'Rating': 'mean',
            'Goals': 'sum',
            'Team_Performance_Drop': 'mean',
            'Injury_Start': 'count'
        }).rename(columns={'Injury_Start': 'Injury_Count'}).reset
