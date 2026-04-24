import logging
import time
from base64 import b64encode

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from extract.settings import settings

logger = logging.getLogger(__name__)

def log_retry_stats(retry_state):
    """
    Callback function to log details before sleeping for a retry.
    """
    # retry_state.attempt_number starts at 1
    # retry_state.outcome holds the exception or result of the last call
    exception = retry_state.outcome.exception()
    logger.warning(
        "Retry n°%d: Error occurred: %s. Retrying in %0.2f seconds...",
        retry_state.attempt_number,
        exception,
        retry_state.next_action.sleep
    )

def is_retryable_error(exception):
    if isinstance(exception, requests.HTTPError):
        return exception.response.status_code in [429, 500, 502, 503, 504]
    return False

class SpotifyApiClient:
    """
    Client HTTP pour l'API Spotify.
    Gère l'authentification OAuth2 client_credentials,
    le renouvellement du token et les retries automatiques.
    """

    def __init__(self):
        self._client_id = settings.CLIENT_ID
        self._client_secret = settings.CLIENT_SECRET
        self._access_token: str | None = None
        self._token_expires_at: float = 0
        self._session = requests.Session()
        self.SPOTIFY_API_BASE = settings.SPOTIFY_API_BASE
        self.SPOTIFY_AUTH_URL = settings.SPOTIFY_AUTH_URL


    def _authenticate(self) -> None:
        """Récupère un token OAuth2 via le flow client_credentials."""
        credentials = b64encode(
            f"{self._client_id}:{self._client_secret}".encode()
        ).decode()

        response = self._session.post(
            self.SPOTIFY_AUTH_URL,
            headers={"Authorization": f"Basic {credentials}"},
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        self._access_token = data["access_token"]
        # On soustrait 30s pour renouveler un peu avant l'expiration réelle
        self._token_expires_at = time.time() + data["expires_in"] - 30
        logger.debug("Token Spotify obtenu, expire dans %ds", data["expires_in"])

    def _ensure_token(self) -> None:
        """Renouvelle le token s'il est absent ou expiré."""
        if not self._access_token or time.time() >= self._token_expires_at:
            self._authenticate()

    @retry(stop=stop_after_attempt(5), 
           wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=retry_if_exception(is_retryable_error),
           before_sleep=log_retry_stats)
    def get(self, endpoint: str, params: dict | None = None) -> dict:
        """
        Effectue un GET sur l'API Spotify.

        Args:
            endpoint: chemin relatif, ex. "/search"
            params: paramètres de query string

        Returns:
            La réponse JSON désérialisée.

        Raises:
            requests.HTTPError: si la réponse est une erreur HTTP non récupérable.
        """
        self._ensure_token()
        url = f"{self.SPOTIFY_API_BASE}{endpoint}"
        logger.debug("GET %s params=%s", url, params)

        response = self._session.get(
            url,
            headers={"Authorization": f"Bearer {self._access_token}"},
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

