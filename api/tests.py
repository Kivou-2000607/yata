import json
import unittest
from django.test import Client
from decouple import config

from bazaar.models import VerifiedClient

class SimpleTest(unittest.TestCase):

    def assertRequestIsJson(self, r):
        r = r.json()

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        # setup verified client for /api/v1/travel/import/
        VerifiedClient.objects.create(
            author_id=42,
            author_name="Torn Player Name",
            name="Tool name",
            version="v1",
            verified=True
        )

    def tearDown(self):
        # Every test needs a client.
        self.client = Client()

        # setup verified client for /api/v1/travel/import/
        VerifiedClient.objects.all().delete()

    def test_get(self):
        # # targets
        # re_path(r'^v1/targets/export/$', targets.exportTargets, name="exportTargets"),
        # re_path(r'^v1/targets/import/$', targets.importTargets, name="importTargets"),
        #
        # # spies
        # re_path(r'^v1/spies/$', spies.getSpies, name="getSpies"),
        # re_path(r'^v1/spies/import/$', spies.importSpies, name="importSpies"),
        # re_path(r'^v1/spy/(?P<target_id>[0-9]*)/$', spies.getSpy, name="getSpy"),
        #
        # # faction
        # re_path(r'^v1/faction/crimes/export/$', faction.getCrimes, name="getCrimes"),
        # re_path(r'^v1/faction/crimes/import/ranking/$', faction.updateRanking, name="updateRanking"),
        # re_path(r'^v1/faction/walls/import/$', faction.importWall, name="importWall"),
        # re_path(r'^v1/faction/livechain/$', faction.livechain, name="livechain"),
        #
        # # auth
        # re_path(r'^v1/auth/$', auth.index, name="auth"),
        #
        # # setup
        # re_path(r'^v1/setup/donations/$', setup.donations, name="donations"),
        # re_path(r'^v1/setup/players/$', setup.players, name="players"),


        parameters = [
            # ('/api/', 302, []),
            # ('/api/v1/', 200, []),
            # ('/api/v1/loot/', 200, ['json']),
            # ('/api/v1/travel/export/', 200, ['json']),
            # ('/api/v1/travel/import/', 400, ['json']),
            (f'/api/v1/targets/export?key={config("SECRET_KEY")}', 200, ['json']),
            # ('/api/v1/targets/import/', 400, ['json']),
        ]
        for url, status_code, extra in parameters:
            r = self.client.get(url)
            print(r.content)
            self.assertEqual(r.status_code, status_code)
            if 'json' in extra:
                self.assertRequestIsJson(r)
            print(f'[test get] {url}: {r.content}')

    def test_travel_import(self):

        payload = {
            "client": "Tool name",
            "version": "v1",
            "author_name": "Kivou",
            "author_id": 2000607,
            "country": "uae",
            "items": [
              {
                  "id": 268,
                  "quantity": 339,
                  "cost": 1000
              },
              {
                  "id": 266,
                  "quantity": 1,
                  "cost": 200
              },
            ]
        }

        r = self.client.post(
            '/api/v1/travel/import/',
            payload,
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 200)
