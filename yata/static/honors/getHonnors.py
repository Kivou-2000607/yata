import cloudscraper
import sys
import os
import requests

honors = requests.get("https://yata.alwaysdata.net/awards/bannersId/").json()

token, agent = cloudscraper.get_cookie_string("https://www.torn.com")
headers = {"User-Agent": agent, "Cookie": token}
for id, key in honors.items():

    image = f"img/{id}.png"
    if not os.path.isfile(image) or not os.path.getsize(image):

        cmd = f'wget -U "{agent}" --header="Accept: text/html" --header="Cookie: {token}" -O {image} https://awardimages.torn.com/{key}.png'
        a = os.system(cmd)
        print(a)
        
        # could make it clean chacking
        if not os.path.getsize(image):
            break
