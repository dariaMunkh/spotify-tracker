import pandas as pd
from rapidfuzz import fuzz, process
 
FEATURE_COLS = [
    "danceability", "energy", "valence", "tempo",
    "acousticness", "instrumentalness", "speechiness", "liveness",
]
 
 
def load_dataset(path="data/audio_features.csv"):
    """
    Load the audio features dataset and precompute a combined search column.
 
    The Kaggle "Spotify Tracks Dataset" (maharshipandya) joins multiple artists
    with ";" (e.g. "Ingrid Michaelson;ZAYN") and has duplicate rows for the
    same track (different album/popularity entries) -- we keep only the first
    occurrence of each track+primary-artist combo, since for matching purposes
    duplicates just add noise.
    """
    df = pd.read_csv(path)
    df = df.dropna(subset=["track_name", "artists"]).reset_index(drop=True)
 
    # Use just the FIRST listed artist for matching -- that's what a playlist's
    # track.artists[0] will give us, and it's the most reliable shared anchor
    # even when the dataset lists several collaborators.
    df["primary_artist"] = df["artists"].str.split(";").str[0].str.strip()
    df["search_key"] = (df["track_name"].str.strip() + " - " + df["primary_artist"]).str.lower()
 
    # Drop exact duplicate (track_name, primary_artist) pairs, keep first
    df = df.drop_duplicates(subset=["search_key"]).reset_index(drop=True)
 
    return df
 
 
def match_track(track_name, artist_name, dataset_df, threshold=75):
    """
    Find the best match for a single track in the dataset.
    Returns the matched row (as a Series) or None if no match clears the threshold.
    """
    query = f"{track_name.strip()} - {artist_name.strip()}".lower()
 
    result = process.extractOne(
        query,
        dataset_df["search_key"],
        scorer=fuzz.token_sort_ratio,
    )
 
    if result is None:
        return None
 
    matched_string, score, idx = result
    if score < threshold:
        return None
 
    return dataset_df.iloc[idx]
 
 
def match_playlist_tracks(playlist_tracks, dataset_df, threshold=75):
    """
    Match a list of playlist tracks (each a dict with "name" and "artist")
    against the dataset.
 
    Returns: (matched_df, unmatched_count)
    """
    matched_rows = []
    unmatched_count = 0
 
    for track in playlist_tracks:
        match = match_track(track["name"], track["artist"], dataset_df, threshold)
        if match is not None:
            matched_rows.append(match)
        else:
            unmatched_count += 1
 
    if matched_rows:
        matched_df = pd.DataFrame(matched_rows).reset_index(drop=True)
    else:
        matched_df = pd.DataFrame(columns=dataset_df.columns)
 
    return matched_df, unmatched_count
 
 
if __name__ == "__main__":
    # Quick smoke test with a fake playlist
    dataset = load_dataset()
 
    fake_playlist = [
        {"name": "Blinding Lights", "artist": "The Weeknd"},
        {"name": "good 4 u", "artist": "Olivia Rodrigo"},
        {"name": "Some Song That Doesnt Exist", "artist": "Nobody"},
        {"name": "watermelon sugar", "artist": "harry styles"},  # lowercase, should still match
    ]
 
    matched, unmatched = match_playlist_tracks(fake_playlist, dataset)
    print(f"Matched {len(matched)} of {len(fake_playlist)} tracks ({unmatched} unmatched)\n")
    print(matched[["track_name", "artists"]])