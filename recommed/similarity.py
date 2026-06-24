import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
 
from recommend.matching import FEATURE_COLS
 
 
def get_recommendations(matched_tracks_df, full_dataset_df, n_recommendations=10):
    """
    Given the user's matched playlist tracks and the full dataset,
    return the top N most similar tracks (excluding tracks already in the playlist).
    """
    if matched_tracks_df.empty:
        return pd.DataFrame(columns=full_dataset_df.columns)
 
    # Fit the scaler on the full dataset so everything is on the same scale
    scaler = StandardScaler()
    full_scaled = scaler.fit_transform(full_dataset_df[FEATURE_COLS])
    matched_scaled = scaler.transform(matched_tracks_df[FEATURE_COLS])
 
    # Average the playlist's scaled feature vectors into one "taste profile"
    playlist_vector = matched_scaled.mean(axis=0).reshape(1, -1)
 
    # Ask for extra neighbors since we'll filter out tracks already in the playlist
    n_neighbors = min(n_recommendations + len(matched_tracks_df) + 5, len(full_dataset_df))
    nn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
    nn_model.fit(full_scaled)
 
    distances, indices = nn_model.kneighbors(playlist_vector)
 
    recommendations = full_dataset_df.iloc[indices[0]].copy()
    recommendations["similarity_score"] = 1 - distances[0]  # cosine distance -> similarity
 
    # Drop anything already in the user's playlist
    already_have = set(matched_tracks_df["search_key"])
    recommendations = recommendations[~recommendations["search_key"].isin(already_have)]
 
    return recommendations.head(n_recommendations).reset_index(drop=True)
 
 
def explain_recommendation(rec_row, matched_tracks_df, top_n=2):
    """
    For a single recommended track, find which input playlist tracks it's
    closest to -- used to show "similar to vibes from: X, Y" in the UI.
    """
    from scipy.spatial.distance import cdist
    import numpy as np
 
    rec_vector = rec_row[FEATURE_COLS].values.reshape(1, -1).astype(float)
    playlist_vectors = matched_tracks_df[FEATURE_COLS].values.astype(float)
 
    distances = cdist(rec_vector, playlist_vectors, metric="cosine")[0]
    closest_idx = np.argsort(distances)[:top_n]
 
    return matched_tracks_df.iloc[closest_idx]["track_name"].tolist()
 
 
if __name__ == "__main__":
    from recommend.matching import load_dataset, match_playlist_tracks
 
    dataset = load_dataset()
 
    fake_playlist = [
        {"name": "Blinding Lights", "artist": "The Weeknd"},
        {"name": "Save Your Tears", "artist": "The Weeknd"},
        {"name": "Levitating", "artist": "Dua Lipa"},
    ]
 
    matched, unmatched = match_playlist_tracks(fake_playlist, dataset)
    print(f"Matched {len(matched)} tracks, {unmatched} unmatched\n")
 
    recs = get_recommendations(matched, dataset, n_recommendations=5)
    print("Recommendations:")
    for _, row in recs.iterrows():
        explanation = explain_recommendation(row, matched)
        print(f"  {row['track_name']} by {row['artists']} (similarity: {row['similarity_score']:.2f}) -- because you have: {', '.join(explanation)}")