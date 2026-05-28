from extract.spotify_api import get_spotify_client, get_top_tracks, get_recently_played
from transform.clean import clean_top_tracks, clean_recently_played
from load.database import save_top_tracks, save_recently_played

def run_pipeline():
    print("Starting pipeline...")

    # Extract
    sp = get_spotify_client()
    raw_top_tracks = get_top_tracks(sp)
    raw_recently_played = get_recently_played(sp)
    print("Data extracted from Spotify")

    # Transform
    clean_tracks = clean_top_tracks(raw_top_tracks)
    clean_recent = clean_recently_played(raw_recently_played)
    print("Data cleaned")

    # Load
    save_top_tracks(clean_tracks)
    save_recently_played(clean_recent)
    print("Pipeline complete!")

if __name__ == "__main__":
    run_pipeline()