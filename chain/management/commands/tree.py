from django.core.management.base import BaseCommand

from django.conf import settings

from chain.models import Faction
from yata.handy import apiCall

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND tree] start")

        for faction in Faction.objects.all():
            print("[COMMAND tree] faction {}".format(faction))

            # get api key
            if faction.apiString == "0":
                print("[COMMAND tree] no api key found")
                break
            factionId = faction.tId
            keyHolder, key = faction.get_random_key()

            # call for upgrades
            upgrades = apiCall('faction', factionId, 'upgrades', key, sub='upgrades')
            if 'apiError' in upgrades:
                print('[COMMAND tree] api key error: {}'.format((upgrades['apiError'])))
                break

            faction = apiCall('faction', factionId, 'basic', key)
            if 'apiError' in faction:
                print('[COMMAND tree] api key error: {}'.format((faction['apiError'])))
                break

            # building upgrades tree
            tree = dict({})
            for k, upgrade in sorted(upgrades.items(), key=lambda x: x[1]['branchorder'], reverse=False):
                if upgrade['branch'] != 'Core':
                    if tree.get(upgrade['branch']) is None:
                        tree[upgrade['branch']] = dict({})
                    tree[upgrade['branch']][upgrade['name']] = upgrade

            tmp = "{} perks".format(faction["name"])
            txt = "{}\n".format(tmp)
            txt += "{}\n".format("-" * len(tmp))
            txt += " {}\n\n".format("-" * (len(tmp) - 2))
            for branch, upgrades in tree.items():
                txt += "* {}\n".format(branch)
                for k, v in upgrades.items():
                    txt += "    {}: {}\n".format(k, v["ability"])
                txt += "\n"

                print('[VIEW tree] {} ({} upgrades)'.format(branch, len(upgrades)))

            txt = txt[:-2]  # delete last \n

            img = Image.new('RGBA', (5000, 5000), color=(255, 0, 0, 0))
            print(settings.STATIC_ROOT + '/perso/font/CourierPolski1941.ttf')
            fnt = ImageFont.truetype(settings.STATIC_ROOT + '/perso/font/CourierPolski1941.ttf', 25)
            d = ImageDraw.Draw(img)
            d.text((10, 10), txt, font=fnt)
            x, y = d.textsize(txt, font=fnt)

            img.crop((0, 0, x + 10 + 10, y + 10 + 10)).save("{}/trees/{}.png".format(settings.STATIC_ROOT, factionId))
            print('[VIEW tree] image saved')
