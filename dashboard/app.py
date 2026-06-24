import streamlit as st
import pandas as pd
import plotly.express as px

from extract.public_playlist import get_client_credentials_token, extract_playlist_id, get_playlist_tracks
from recommend.matching import load_dataset, match_playlist_tracks
from recommend.similarity import get_recommendations, explain_recommendation

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

# --- Section 5: Playlist Recommender (the part anyone can use, no login needed) ---
st.divider()
st.subheader("🔎 Find songs similar to YOUR playlist")
st.markdown("Paste any public Spotify playlist link and get song recommendations based on its overall vibe.")

playlist_url = st.text_input("Spotify playlist link", placeholder="https://open.spotify.com/playlist/...")
go = st.button("Get Recommendations", type="primary")

if go:
    if not playlist_url:
        st.error("Paste a playlist link first.")
    else:
        playlist_id = extract_playlist_id(playlist_url)
        if not playlist_id:
            st.error("Couldn't read that link. Make sure it's a public Spotify playlist URL.")
        else:
            try:
                with st.spinner("Reading your playlist..."):
                    token = get_client_credentials_token()
                    playlist_tracks = get_playlist_tracks(playlist_id, token)

                if not playlist_tracks:
                    st.warning("That playlist looks empty, or it might be private.")
                else:
                    with st.spinner("Matching tracks and finding similar songs..."):
                        dataset = load_dataset()
                        matched, unmatched_count = match_playlist_tracks(playlist_tracks, dataset)

                    if matched.empty:
                        st.warning("Couldn't match any songs from this playlist to our dataset. Try a different playlist!")
                    else:
                        st.success(f"Matched {len(matched)} of {len(playlist_tracks)} songs "
                                   f"({unmatched_count} not found in our dataset)")

                        recs = get_recommendations(matched, dataset, n_recommendations=10)

                        st.markdown("#### Recommended for you")
                        for i, row in recs.iterrows():
                            because = explain_recommendation(row, matched)
                            col1, col2 = st.columns([5, 1])
                            with col1:
                                st.write(f"**{row['track_name']}** — {row['artists']}")
                                st.caption(f"Similar to: {', '.join(because)}")
                            with col2:
                                st.button("👍", key=f"up_{i}")
                                st.button("👎", key=f"down_{i}")

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong: {e}")