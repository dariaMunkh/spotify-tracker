import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

def get_spotify_client():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-top-read user-read-recently-played"
    ))
    return sp

def get_top_tracks(sp, limit=50):
    results = sp.current_user_top_tracks(limit=limit, time_range="short_term")
    tracks = []
    for item in results["items"]:
        track = {
            "id": item["id"],
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "album": item["album"]["name"],
            "popularity": item["popularity"]
        }
        tracks.append(track)
    return tracks

if __name__ == "__main__":
    sp = get_spotify_client()
    tracks = get_top_tracks(sp)
    for track in tracks[:5]:
        print(track)