import logging

from extract.api.api_client import SpotifyApiClient
from extract.models import Album

MAX_LIMIT = 10
MAX_OFFSET = 1000

class AlbumService:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_albums_by_artist(
        self,
        client: SpotifyApiClient,
        artist_id: str,
        market: str,
        max_results: int = 30,
    ) -> list[Album]:
        """
        Récupère les albums d'un artiste via /artists/{id}/albums.

        Args:
            client: instance de SpotifyApiClient
            artist_id: spotify_id de l'artiste
            market: code pays ISO 3166-1, ex. "FR"
            max_results: nombre maximum d'albums à retourner

        Returns:
            Liste d'Album dédoublonnés par spotify_id.
        """
        albums: dict[str, Album] = {}
        offset = 0

        while len(albums) < max_results and offset < MAX_OFFSET:
            remaining = max_results - len(albums)
            current_limit = min(MAX_LIMIT, remaining)

            data = client.get(
                f"/artists/{artist_id}/albums",
                params={
                    "market": market,
                    "limit": current_limit,
                    "offset": offset,
                    "include_groups": "album",
                },
            )

            items = data.get("items", [])
            if not items:
                self.logger.info("Aucun album supplémentaire pour artist_id=%s, arrêt.", artist_id)
                break

            for item in items:
                album = self._parse_album(item, artist_id=artist_id)
                if album and album.spotify_id not in albums:
                    albums[album.spotify_id] = album

            total_available = data.get("total", 0)
            offset += current_limit

            if offset >= total_available:
                break

        self.logger.info("%d albums récupérés pour artist_id=%s", len(albums), artist_id)
        return list(albums.values())


    def _parse_album(self, item: dict, artist_id: str) -> Album | None:
        """
        Convertit un objet album brut de l'API en modèle SQLAlchemy Album.
        Retourne None si les champs obligatoires sont absents.
        """
        spotify_id = item.get("id")
        name = item.get("name")

        if not spotify_id or not name:
            self.logger.warning("Album ignoré : champs id ou name manquants. item=%s", item)
            return None

        images = item.get("images", [])
        image_url = images[0].get("url") if images else None

        return Album(
            spotify_id=spotify_id,
            name=name,
            release_date=item.get("release_date"),
            image_url=image_url,
            total_tracks=item.get("total_tracks"),
            album_type=item.get("album_type"),
            spotify_url=item.get("external_urls", {}).get("spotify"),
            artist_id=artist_id,
        )