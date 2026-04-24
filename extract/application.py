
import logging
import os
import sys

from sqlalchemy import create_engine, engine

from extract.services.album_service import AlbumService
from extract.services.titre_service import TitreService
from extract.settings import settings
from extract.api.api_client import SpotifyApiClient
from extract.services.artist_service import ArtistService
from extract.services.loader import LoaderService

class Application:
    def __init__(self):
        self.client = SpotifyApiClient()
        self.loader_service = LoaderService()
        self.engine = create_engine(settings.DATABASE_URL)
        self.loader_service._ensure_schema(self.engine)

        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                    logging.FileHandler("logs/python.log"), # Fichier log
                    logging.StreamHandler(sys.stdout)       # Terminal
    ]
        )
        self.logger = logging.getLogger(__name__)

        self.album_service = AlbumService()
        self.artist_service = ArtistService()
        self.titre_service = TitreService()

    def run(self) -> None:
        self.logger.info("Démarrage du job d'extraction Spotify.")

        all_artists = []
        for genre in settings.GENRES:
            self.logger.info("Traitement du genre : %s", genre)

            artists = self.artist_service.get_artists_by_genre(
                client=self.client,
                genre=genre,
                market=settings.MARKET,
                max_results=settings.ARTISTS_PER_GENRE,
            )
            all_artists.extend(artists)

        self.loader_service.load(all_artists, self.engine)
        
        all_albums = []
        for artist in all_artists:
            albums = self.album_service.get_albums_by_artist(
                client=self.client,
                artist_id=artist.spotify_id,
                market=settings.MARKET,
                max_results=settings.ALBUM_PER_ARTIST,
            )
            all_albums.extend(albums)

        self.loader_service.load(all_albums, self.engine)

        all_titres = []
        for album in all_albums:
            titres = self.titre_service.get_titres_by_album(
                client=self.client,
                album_id=album.spotify_id,
                market=settings.MARKET,
                max_results=settings.TITRES_PER_ALBUM,
            )
            all_titres.extend(titres)

        self.loader_service.load(all_titres, self.engine)
        
        self.logger.info("Job terminé.")


if __name__ == "__main__":
    app = Application()
    app.run()
