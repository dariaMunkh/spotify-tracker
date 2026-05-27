import pandas as pd 
from datetime import datetime

def clean_top_tracks(tracks):
  df = pd.DataFrame(tracks)
  df = df.drop_duplicates(subset="id")
  df.columns = [col.lower() for col in df.columns]
  df["date_pulled"] = datetime.today().strftime("%Y-%m-%d")
  return df

def clean_recently_played(tracks):
    df = pd.DataFrame(tracks)
    df = df.drop_duplicates(subset=["id", "played_at"])
    df.columns = [col.lower() for col in df.columns]
    df["played_at"] = pd.to_datetime(df["played_at"])
    df["date_pulled"] = datetime.today().strftime("%Y-%m-%d")
    return df

if __name__ == "__main__":
    # Test with dummy data
    sample_tracks = [
        {"id": "abc", "name": "Song 1", "artist": "Artist 1", "album": "Album 1", "popularity": 80},
        {"id": "abc", "name": "Song 1", "artist": "Artist 1", "album": "Album 1", "popularity": 80},
        {"id": "def", "name": "Song 2", "artist": "Artist 2", "album": "Album 2", "popularity": 60},
    ]
    df = clean_top_tracks(sample_tracks)
    print(df)
    print(f"\nShape: {df.shape}")