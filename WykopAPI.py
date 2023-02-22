import config

import requests
import json

SERVER = 'https://wykop.pl/api/v3/'

class WykopAPI:

    def __init__(self):
        self.token = self.post_auth()
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + self.token})

    def post_auth(self):
        request_body = {
            "data": {
                "key": config.KEY,
                "secret": config.SECRETKEY
            }
        }

        response = requests.post(SERVER + 'auth', json=request_body)
        token = response.json()['data']['token']
        return token

    def get_links(self, page="1", sort="newest", type="upcoming"):
        query = SERVER + 'links' + '?page=' + page + '&sort=' + sort + '&type=' + type
        response = self.session.get(query)
        return response

    def get_connect(self):
        response = self.session.get(SERVER + 'connect')
        return response

    def post_entry(self, request_body):
        response = self.session.post(SERVER + 'entries', json=request_body)
        return response

    def post_refresh_token(self):

        with open('rToken', 'r') as file:
            config.USER_RTOKEN = file.read().strip()

        request_body = {
            "data": {
                "refresh_token": config.USER_RTOKEN
            }
        }
        response = requests.post(SERVER + 'refresh-token', json=request_body)

        config.USER_TOKEN = response.json()['data']['token']
        config.USER_RTOKEN = response.json()['data']['refresh_token']

        with open('rToken', 'w') as file:
            file.write(config.USER_RTOKEN)

        with open('Token', 'w') as file:
            file.write(config.USER_TOKEN)