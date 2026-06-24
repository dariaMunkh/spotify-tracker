import re
import base64
import os
import requests
from dotenv import load_dotenv
 
load_dotenv()
 
 
def get_client_credentials_token():
    """Get an app-only access token. No user login involved."""
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
 
    auth_str = f"{client_id}:{client_secret}"
    auth_bytes = base64.b64encode(auth_str.encode()).decode()
 
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth_bytes}"},
        data={"grant_type": "client_credentials"},
    )
    response.raise_for_status()
    return response.json()["access_token"]
 
 
def extract_playlist_id(url_or_id):
    """Pull the playlist ID out of a full Spotify URL, or pass through if it's already an ID."""
    match = re.search(r"playlist[/:]([a-zA-Z0-9]+)", url_or_id)
    if match:
        return match.group(1)
    # Assume they pasted a bare ID
    if re.fullmatch(r"[a-zA-Z0-9]+", url_or_id.strip()):
        return url_or_id.strip()
    return None
 
 
def get_playlist_tracks(playlist_id, token):
    """
    Fetch all tracks from a public playlist.
    Uses /items (not the old /tracks path -- that was renamed in the Feb 2026 API changes).
    """
    headers = {"Authorization": f"Bearer {token}"}
    tracks = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items"
    params = {"limit": 50, "fields": "items(track(name,artists(name))),next"}
 
    while url:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 404:
            raise ValueError("Playlist not found -- check that the link is correct and the playlist is public.")
        resp.raise_for_status()
        data = resp.json()
 
        for item in data.get("items", []):
            track = item.get("track")
            if track and track.get("name"):
                tracks.append({
                    "name": track["name"],
                    "artist": track["artists"][0]["name"] if track.get("artists") else "",
                })
 
        url = data.get("next")
        params = None  # params are baked into the "next" URL already
 
    return tracks
 
 
if __name__ == "__main__":
    # Smoke test -- replace with a real public playlist ID to test against the live API
    token = get_client_credentials_token()
    print("Got token successfully" if token else "Token fetch failed")