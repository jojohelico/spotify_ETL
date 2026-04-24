import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    genres_raw = os.environ.get("SPOTIFY_GENRES", "rock,pop,jazz")
    GENRES = [g.strip() for g in genres_raw.split(",") if g.strip()]
    ARTISTS_PER_GENRE = int(os.environ.get("SPOTIFY_ARTISTS_PER_GENRE", "5"))
    ALBUM_PER_ARTIST = int(os.environ.get("SPOTIFY_ALBUM_PER_ARTIST", "5"))
    TITRES_PER_ALBUM = int(os.environ.get("SPOTIFY_TITRES_PER_ALBUM", "5"))

    CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
    MARKET = os.environ.get("SPOTIFY_MARKET", "FR")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SPOTIFY_AUTH_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_BASE = "https://api.spotify.com/v1"

settings = Settings()