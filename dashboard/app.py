import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_top_tracks():
    return pd.read_csv("data/top_tracks.csv")

@st.cache_data
def load_recently_played():
    df = pd.read_csv("data/recently_played.csv")
    df["played_at"] = pd.to_datetime(df["played_at"])
    return df

# Page config
st.set_page_config(page_title="Spotify Tracker", page_icon="🎵", layout="wide")

# Header
st.title("🎵 My Spotify Tracker")
st.markdown("A live dashboard of my Spotify listening habits")

# Load data
top_tracks = load_top_tracks()
recently_played = load_recently_played()

# --- Section 1: Top Tracks ---
st.subheader("🏆 My Top Tracks")
top_tracks["rank"] = range(1, len(top_tracks) + 1)
fig1 = px.bar(
    top_tracks.head(10),
    x="name",
    y="rank",
    color="artist",
    title="My Top 10 Tracks (1 = most played)"
)
fig1.update_yaxes(autorange="reversed")
st.plotly_chart(fig1, use_container_width=True)

# --- Section 2: Recently Played ---
st.subheader("🕐 Recently Played")
st.dataframe(recently_played[["name", "artist", "album", "played_at"]].head(20))

# --- Section 3: Top Artists ---
st.subheader("🎤 Most Played Artists")
artist_counts = recently_played["artist"].value_counts().reset_index()
artist_counts.columns = ["artist", "play_count"]
fig2 = px.bar(
    artist_counts.head(10),
    x="artist",
    y="play_count",
    color="artist",
    title="Top 10 Most Played Artists"
)
st.plotly_chart(fig2, use_container_width=True)

# --- Section 4: Listening Activity ---
st.subheader("📅 Listening Activity Over Time")
recently_played["date"] = recently_played["played_at"].dt.date
daily_counts = recently_played.groupby("date").size().reset_index(name="songs_played")
fig3 = px.line(
    daily_counts,
    x="date",
    y="songs_played",
    title="Songs Played Per Day"
)
st.plotly_chart(fig3, use_container_width=True)