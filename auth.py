"""Helper: pobierz URL do autoryzacji użytkownika przez /connect.

Uruchom ten skrypt raz, aby sparować swoje konto z aplikacją.
Po przejściu procesu connect otrzymasz refresh token, który zapisz do pliku 'rToken'.
"""

import WykopAPI

api = WykopAPI.WykopAPI()
result = api.get_connect()
connect_url = result.get("data", {}).get("connect_url", str(result))
print("Otwórz poniższy URL w przeglądarce aby połączyć konto:")
print(connect_url)
print("\nPo autoryzacji skopiuj 'rtoken' z paska adresu (lub strony powrotnej)")
print("i ustaw wpis w pliku .env jako:\nWYKOP_USER_REFRESH_TOKEN=skopiowany_rtoken")