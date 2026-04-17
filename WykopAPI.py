import os
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key

ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)

SERVER = "https://wykop.pl/api/v3/"


class WykopAPI:
    """Wrapper for Wykop API v3.

    Auth flow:
      1. __init__  -> POST /auth  (app key+secret -> app token, stored in session)
      2. refresh_user_token() -> POST /refresh-token (refresh token -> user token,
         session header is swapped to user token so subsequent calls act as the user)
    """

    def __init__(self):
        self.session = requests.Session()
        self._app_token = self._authenticate_app()
        self.user_token = None
        self.session.headers.update({"Authorization": f"Bearer {self._app_token}"})

    # ------------------------------------------------------------------ auth
    def _authenticate_app(self) -> str:
        """POST /auth – get an app-level JWT using app key & secret."""
        body = {
            "data": {
                "key": os.environ["WYKOP_APP_KEY"],
                "secret": os.environ["WYKOP_APP_SECRET"],
            }
        }
        resp = requests.post(f"{SERVER}auth", json=body)
        resp.raise_for_status()
        return resp.json()["data"]["token"]

    def refresh_user_token(self) -> str:
        """POST /refresh-token – exchange a refresh token for a new user JWT.

        * Uses self.session (which carries the app Bearer token) as required by the API.
        * After success the session header is swapped to the NEW user token
          so all further requests (get_links, post_entry, …) act as the user.
        * Both tokens are persisted to disk for the next run.
        """
        refresh_token = self._load_refresh_token()

        body = {"data": {"refresh_token": refresh_token}}
        # Do not use self.session here! Wykop API throws 'application_not_permission'
        # if you pass the application Bearer token to /refresh-token.
        resp = requests.post(f"{SERVER}refresh-token", json=body)
        resp.raise_for_status()

        data = resp.json()["data"]
        self.user_token = data["token"]
        new_refresh_token = data["refresh_token"]

        self._save_tokens(self.user_token, new_refresh_token)
        return self.user_token

    # --------------------------------------------------------------- endpoints
    def get_links(self, page: str = "1", sort: str = "newest",
                  link_type: str = "upcoming") -> dict:
        """GET /links – returns parsed JSON directly."""
        resp = self.session.get(
            f"{SERVER}links",
            params={"page": page, "sort": sort, "type": link_type},
        )
        resp.raise_for_status()
        return resp.json()

    def post_entry(self, content: str, adult: bool = False) -> dict:
        """POST /entries – create a new mikroblog entry."""
        if not self.user_token:
            raise ValueError("Brak tokena użytkownika, wywołaj najpierw refresh_user_token()")
            
        body = {"data": {"content": content, "adult": adult}}
        headers = {"Authorization": f"Bearer {self.user_token}"}
        resp = requests.post(f"{SERVER}entries", json=body, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def get_connect(self) -> dict:
        """GET /connect – returns the connect/OAuth URL info."""
        resp = self.session.get(f"{SERVER}connect")
        resp.raise_for_status()
        return resp.json()

    # ---------------------------------------------------------- token helpers
    @staticmethod
    def _load_refresh_token() -> str:
        # Load directly from OS environment or reload dotenv just in case
        load_dotenv(ENV_PATH, override=True)
        rtoken = os.environ.get("WYKOP_USER_REFRESH_TOKEN")
        if not rtoken:
            raise FileNotFoundError(
                "Brak parametru WYKOP_USER_REFRESH_TOKEN w pliku .env!\n"
                "Uruchom najpierw auth.py, wejdź w link autoryzacyjny i wklej zwrócony 'rtoken'."
            )
        return rtoken.strip()

    @staticmethod
    def _save_tokens(access_token: str, refresh_token: str) -> None:
        # Save tokens into .env to keep everything in one place
        set_key(str(ENV_PATH), "WYKOP_USER_TOKEN", access_token)
        set_key(str(ENV_PATH), "WYKOP_USER_REFRESH_TOKEN", refresh_token)