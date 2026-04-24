import logging

from extract.api.api_client import SpotifyApiClient
from extract.models import Titre

MAX_LIMIT = 10
MAX_OFFSET = 1000

class TitreService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_titres_by_album(
        self, 
        client: SpotifyApiClient,
        album_id: str,
        market: str,
        max_results: int = 100,
    ) -> list[Titre]:

        titres: dict[str, Titre] = {}
        offset = 0

        while len(titres) < max_results and offset < MAX_OFFSET:
            remaining = max_results - len(titres)
            current_limit = min(MAX_LIMIT, remaining)

            data = client.get(
                f"/albums/{album_id}/tracks",
                params={
                    "market": market,
                    "limit": current_limit,
                    "offset": offset,
                },
            )

            items = data.get("items", [])
            if not items:
                self.logger.info("Aucun titre supplémentaire pour album_id=%s, arrêt.", album_id)
                break

            for item in items:
                titre = self._parse_titre(item, album_id=album_id)
                if titre and titre.spotify_id not in titres:
                    titres[titre.spotify_id] = titre

            total_available = data.get("total", 0)
            offset += current_limit

            if offset >= total_available:
                break

        self.logger.info("%d titres récupérés pour album_id=%s", len(titres), album_id)
        return list(titres.values())


    def _parse_titre(self, item: dict, album_id: str) -> Titre | None:
        spotify_id = item.get("id")
        name = item.get("name")

        if not spotify_id or not name:
            self.logger.warning("Titre ignoré : champs id ou name manquants. item=%s", item)
            return None

        return Titre(
            spotify_id=spotify_id,
            name=name,
            spotify_url=item.get("external_urls", {}).get("spotify"),
            is_playable=item.get("is_playable"),
            explicit=item.get("explicit"),
            track_number=item.get("track_number"),
            duration_ms=item.get("duration_ms"),
            album_id=album_id,
        )