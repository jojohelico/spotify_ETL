import pytest
from unittest.mock import MagicMock

from extract.services.album_service import AlbumService


@pytest.fixture
def service():
    """Instancie le service avec un logger mocké."""
    s = AlbumService()
    s.logger = MagicMock()
    return s


@pytest.fixture
def item_valide():
    """Objet album complet tel que renvoyé par l'API Spotify."""
    return {
        "id": "abc123",
        "name": "Random Access Memories",
        "release_date": "2013-05-17",
        "total_tracks": 13,
        "album_type": "album",
        "images": [{"url": "https://i.scdn.co/image/abc.jpg"}],
        "external_urls": {"spotify": "https://open.spotify.com/album/abc123"},
    }


# --- Teste le comportement attendu ---

def test_parse_album_retourne_un_album(service, item_valide):
    album = service._parse_album(item_valide, artist_id="artist_xyz")
    assert album is not None


def test_parse_album_mappe_les_champs_correctement(service, item_valide):
    album = service._parse_album(item_valide, artist_id="artist_xyz")
    assert album.spotify_id == "abc123"
    assert album.name == "Random Access Memories"
    assert album.release_date == "2013-05-17"
    assert album.total_tracks == 13
    assert album.album_type == "album"
    assert album.image_url == "https://i.scdn.co/image/abc.jpg"
    assert album.spotify_url == "https://open.spotify.com/album/abc123"
    assert album.artist_id == "artist_xyz"


# --- Champs optionnels ---

def test_parse_album_sans_release_date(service, item_valide):
    del item_valide["release_date"] # Supprime le champ release_date
    album = service._parse_album(item_valide, artist_id="artist_xyz")
    assert album.release_date is None


# --- Champs obligatoires manquants ---

def test_parse_album_sans_id_retourne_none(service, item_valide):
    del item_valide["id"]
    album = service._parse_album(item_valide, artist_id="artist_xyz")
    assert album is None


def test_parse_album_id_vide_retourne_none(service, item_valide):
    item_valide["id"] = ""
    album = service._parse_album(item_valide, artist_id="artist_xyz")
    assert album is None


def test_parse_album_sans_id_ni_name_log_un_warning(service, item_valide):
    del item_valide["id"]
    del item_valide["name"]
    service._parse_album(item_valide, artist_id="artist_xyz")
    service.logger.warning.assert_called_once()