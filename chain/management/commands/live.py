from django.core.management.base import BaseCommand
from django.utils import timezone

from chain.models import Faction
from yata.handy import apiCall
from yata.handy import timestampToDate

from chain.functions import apiCallAttacks
from chain.functions import fillReport
from chain.functions import updateMembers


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND live] start")

        for faction in Faction.objects.all():
            print("[COMMAND live] faction {}".format(faction))

            # get api key
            if faction.apiString == "0":
                print("[COMMAND live] no api key found")
                continue
            factionId = faction.tId
            keyHolder, key = faction.get_random_key()
            print("[COMMAND live] using {} api key".format(keyHolder))

            # get chain status
            liveChain = apiCall("faction", factionId, "chain", key, sub="chain")
            if 'apiError' in liveChain:
                print('[COMMAND live] api key error: {}'.format((liveChain['apiError'])))
                continue

            if not bool(liveChain["current"]):
                print("[COMMAND live] no active chain")
                faction.chain_set.filter(tId=0).delete()
                print("[COMMAND live] report 0 deleted")
                continue

            # get chain
            print('[COMMAND live] this is a live report')
            chain = faction.chain_set.filter(tId=0).first()
            if chain is None:
                print('[COMMAND live] create chain 0')
                chain = faction.chain_set.create(tId=0)

            # change dates and status
            chainInfo = apiCall('faction', factionId, 'chain', key, sub='chain')
            if 'apiError' in chainInfo:
                print('[COMMAND live] api key error: {}'.format((chainInfo['apiError'])))
                continue
            chain.status = True
            chain.end = int(timezone.now().timestamp())
            chain.endDate = timestampToDate(chain.end)
            chain.start = int(chainInfo.get("start"))
            chain.startDate = timestampToDate(chain.start)
            chain.save()

            # delete old report and create new
            chain.report_set.all().delete()
            report = chain.report_set.create()

            keyHolder, key = faction.get_random_key()
            attacks = apiCallAttacks(faction, chain, key=key)
            print('[COMMAND live] new report created')

            # update members
            members = updateMembers(faction)
            if 'apiError' in members:
                print("[COMMAND live] error in API continue to next chain: {}", members['apiError'])
                continue

            fillReport(faction, members, chain, report, attacks)

            print("[COMMAND live] end")
