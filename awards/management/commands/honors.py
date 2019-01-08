from django.core.management.base import BaseCommand
from django.conf import settings

import json
import os
from yata.honors import d
from yata.honors import ts

class Command(BaseCommand):
    def handle(self, **options):
        file = os.path.join(settings.PROJECT_ROOT, 'static/honors/bannersId.json')
        with open(file, 'w') as fp:
            json.dump(d, fp)

        file = os.path.join(settings.PROJECT_ROOT, 'static/honors/bannersIdTS.json')
        with open(file, 'w') as fp:
            json.dump(ts, fp)

        n_ok = 0
        n_nok = 0
        n_ts = 0
        n_all = len(d)
        for k, v in d.items():
            if v:
                n_ok += 1
            else:
                if k in ts:
                    if ts[k]:
                        n_ts += 1
                    else:
                        n_nok += 1
                else:
                    n_nok += 1

        print("Total = {}, ok = {} ({:.01f} %), ts = {}, nok = {}".format(n_all, n_ok, 100*n_ok/float(n_all), n_ts, n_nok))
        print("TS length = {}".format(len(ts)))

        tsId = [v for k, v in ts.items()]
        toDel = []
        for img in os.listdir(os.path.join(settings.PROJECT_ROOT, 'static/honors/tsimg')):
            splt = img.split(".")
            if splt[-1] == "png":
                if splt[0] not in tsId:
                    toDel.append(img)
        print("Images not in ts: {}".format(" ".join(toDel)))
