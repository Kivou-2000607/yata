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

            bridge = {"Criminality": 0,
                      "Fortitude": 1,
                      "Voracity": 2,
                      "Toleration": 3,
                      "Excursion": 4,
                      "Steadfast": 5,
                      "Aggression": 6,
                      "Suppression": 7,
                    }

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


            # create image background
            img = Image.new('RGBA', (5000, 5000), color=(255, 0, 0, 0))
            # img = Image.new('RGB', (5000, 5000), color=(0, 0, 0))
            fnt = ImageFont.truetype(settings.STATIC_ROOT + '/perso/font/CourierPolski1941.ttf', 25)
            d = ImageDraw.Draw(img)

            # add title
            tmp = "{} perks".format(faction["name"])
            txt = "{}\n".format(tmp)
            txt += "{}\n".format("-" * len(tmp))
            txt += " {}\n\n".format("-" * (len(tmp) - 2))
            d.text((10, 10), txt, font=fnt)
            x, y = d.textsize(txt, font=fnt)
            print(x, y)
            for branch, upgrades in tree.items():

                icon = Image.open(settings.STATIC_ROOT + '/trees/tier_unlocks_b{}_t2.png'.format(bridge[branch]))
                img.paste(icon, (10, y+10))

                txt = ""
                txt += "  {}\n".format(branch)
                for k, v in upgrades.items():
                    txt += "    {}: {}\n".format(k, v["ability"])
                txt += "\n"

                d.text((90, 10+y), txt, font=fnt)
                xTmp, yTmp = d.textsize(txt, font=fnt)
                x = max(xTmp, x)
                y += yTmp
                print(x, y)

                print('[VIEW tree] {} ({} upgrades)'.format(branch, len(upgrades)))

            # txt = txt[:-2]  # delete last \n

            #

            # for branch in tree:

            img.crop((0, 0, x + 90 + 10, y + 10 + 10)).save("{}/trees/{}.png".format(settings.STATIC_ROOT, factionId))
            # img.save("{}/trees/{}.png".format(settings.STATIC_ROOT, factionId))
            print('[VIEW tree] image saved')
