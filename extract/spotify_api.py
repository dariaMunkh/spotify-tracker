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
            "popularity": item.get("popularity", 0)
        }
        tracks.append(track)
    return tracks

def get_recently_played(sp, limit=50):
    results = sp.current_user_recently_played(limit=limit)
    tracks = []
    for item in results["items"]:
        track = {
            "id": item["track"]["id"],
            "name": item["track"]["name"],
            "artist": item["track"]["artists"][0]["name"],
            "album": item["track"]["album"]["name"],
            "played_at": item["played_at"]
        }
        tracks.append(track)
    return tracks

if __name__ == "__main__":
    sp = get_spotify_client()

    print("--- TOP TRACKS ---")
    tracks = get_top_tracks(sp)
    for track in tracks[:5]:
        print(track)

    print("\n--- RECENTLY PLAYED ---")
    recent = get_recently_played(sp)
    for track in recent[:5]:
        print(track)