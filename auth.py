import requests
import json
import random

import config
import WykopAPI


wykopApi = WykopAPI.WykopAPI()

res = wykopApi.get_connect()
print(res.json())