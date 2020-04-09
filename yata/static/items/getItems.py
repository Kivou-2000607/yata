import cloudscraper
import sys
import os

for id in range(25:50):
    print(id)
    # token, agent = cloudscraper.get_cookie_string("https://www.torn.com")
    # headers = {"User-Agent": agent, "Cookie": token}
    #
    # image = f"img/{id}.png"
    # if not os.path.isfile(image):
    #     cmd = f'wget -U "{agent}" --header="Accept: text/html" --header="Cookie: {token}" -O {image} https://awardimages.torn.com/{key}.png'
    #     os.system(cmd)
