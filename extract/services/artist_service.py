import logging
import pprint

from extract.api.api_client import SpotifyApiClient
from extract.models import Artist


MAX_LIMIT = 10          # limite max acceptée par l'endpoint /search
MAX_OFFSET = 1000       # limite max de pagination de Spotify

class ArtistService:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_artists_by_genre(
        self,
        client: SpotifyApiClient,
        genre: str,
        market: str,
        max_results: int = 100,
    ) -> list[Artist]:
        """
        Récupère des artistes pour un genre donné via l'endpoint /search.

        Spotify ne propose pas d'endpoint dédié "artistes par genre" —
        on passe par la recherche avec le filtre genre:.

        Args:
            client: instance de SpotifyApiClient
            genre: genre musical, ex. "rock", "hip hop"
            market: code pays ISO 3166-1, ex. "FR"
            max_results: nombre maximum d'artistes à retourner

        Returns:
            Liste d'Artist (modèles SQLAlchemy) dédoublonnés par spotify_id.
        """
        artists: dict[str, Artist] = {}
        offset = 0

        while len(artists) < max_results and offset < MAX_OFFSET:
            remaining = max_results - len(artists)
            current_limit = min(MAX_LIMIT, remaining)

            self.logger.info(
                "Recherche artistes genre=%r market=%s offset=%d limit=%d",
                genre,
                market,
                offset,
                current_limit,
            )

            data = client.get(
                "/search",
                params={
                    "q": f"genre:{genre}",
                    "type": "artist",
                    "market": market,
                    "limit": current_limit,
                    "offset": offset,
                },
            )

            items = data.get("artists", {}).get("items", [])
            if not items:
                self.logger.info("Aucun résultat supplémentaire pour genre=%r, arrêt.", genre)
                break

            for item in items:
                artist = self._parse_artist(item, source_genre=genre)
                if artist and artist.spotify_id not in artists:
                    artists[artist.spotify_id] = artist

            total_available = data.get("artists", {}).get("total", 0)
            offset += current_limit

            if offset >= total_available:
                break

        self.logger.info("%d artistes récupérés pour genre=%r", len(artists), genre)
        return list(artists.values())


    def _parse_artist(self, item: dict, source_genre: str) -> Artist | None:
        """
        Convertit un objet artiste brut de l'API en modele SQLAlchemy Artist.
        Retourne None si les champs obligatoires sont absents.
        """
        spotify_id = item.get("id")
        name = item.get("name")

        if not spotify_id or not name:
            self.logger.warning("Artiste ignoré : champs id ou name manquants. item=%s", item)
            return None

        images = item.get("images", [])
        image_url = images[0].get("url") if images else None

        return Artist(
            spotify_id=spotify_id,
            name=name,
            genres=item.get("genres", []),
            image_url=image_url,
            spotify_url=item.get("external_urls", {}).get("spotify"),
            source_genre=source_genre,
        )