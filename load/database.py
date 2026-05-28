import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="spotify_tracker",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        port="5432"
    )
    return conn

def save_top_tracks(df):
    conn = get_db_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO top_tracks (id, name, artist, album, popularity, date_pulled)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                popularity = EXCLUDED.popularity,
                date_pulled = EXCLUDED.date_pulled
        """, (row["id"], row["name"], row["artist"], row["album"], row["popularity"], row["date_pulled"]))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved {len(df)} top tracks to database")

def save_recently_played(df):
    conn = get_db_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO recently_played (id, name, artist, album, played_at, date_pulled)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id, played_at) DO NOTHING
        """, (row["id"], row["name"], row["artist"], row["album"], row["played_at"], row["date_pulled"]))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved {len(df)} recently played tracks to database")