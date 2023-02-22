import requests
import random

import config
import WykopAPI

wykopApi = WykopAPI.WykopAPI()

wykopApi.post_refresh_token()

links = wykopApi.get_links("1", "newest", "homepage")

links = links.json()
data = links['data']

links = []

for link in data:
    print(link)
    print()

for element in data:
    if 'title' in element:
        links.append((element['title'], element['id']))

random_links = [('A', 0), ('B', 0)]

while random_links[0][0].find(' ') == -1 or random_links[1][0].find(' ') == -1:
    random_links = random.sample(links, 2)


spaces = [[pos for pos, char in enumerate(link[0]) if char == ' '] for link in random_links]
middle_spaces = [space[len(space)//2] for space in spaces]

new_title = random_links[0][0][:middle_spaces[0]] + random_links[1][0][middle_spaces[1]:]

# content format

# **new_title**

# [random_links[0][0]](https://www.wykop.pl/link/ + random_links[0][1])
# [random_links[1][0]](https://www.wykop.pl/link/ + random_links[1][1])

# O co w tym chodzi?
# Jestem botem i losowo tworzę "zdanie" łącząc 2 tytuły z popularnych znalezisk.

# Tag do obserwowania / czarnolistowania #dwielinie

content = f"**{new_title}**\n\n[{random_links[0][0]}](https://www.wykop.pl/link/{random_links[0][1]})\n[{random_links[1][0]}](https://www.wykop.pl/link/{random_links[1][1]})\n\nO co w tym chodzi?\nJestem botem i losowo tworzę \"zdanie\" łącząc 2 tytuły z popularnych znalezisk.\n\nTag do obserwowania / czarnolistowania #dwielinie"

headers = {
    "Authorization": f"Bearer {config.USER_TOKEN}",
}

body = {
  "data": {
    "content": content,
    "adult": False
  }
}

#response = requests.post(WykopAPI.SERVER + 'entries', json=body, headers=headers)
#print(response.json())