from django.core.management.base import BaseCommand
from django.utils import timezone

from chain.models import Faction
from yata.handy import apiCall
from yata.handy import apiCallAttacks
from yata.handy import timestampToDate

from yata.handy import fillReport


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND live] start")

        for faction in Faction.objects.all():
            print("[COMMAND live] faction {}".format(faction))

            # get api key
            if faction.apiString == "0":
                print("[COMMAND live] no api key found")
                break
            factionId = faction.tId
            keyHolder, key = faction.get_random_key()

            # get chain status
            print("[COMMAND live] with {} api key".format(keyHolder))
            liveChain = apiCall("faction", factionId, "chain", key, sub="chain")
            if 'apiError' in liveChain:
                print('[COMMAND live] api key error: {}'.format((liveChain['apiError'])))
                break

            if not bool(liveChain["current"]):
                print("[COMMAND live] no active chain")
                faction.chain_set.filter(tId=0).delete()
                print("[COMMAND live] report 0 deleted")
                break

            # get chain
            print('[COMMAND live] this is a live report')
            chain = faction.chain_set.filter(tId=0).first()
            if chain is None:
                print('[COMMAND live] create chain 0')
                chain = faction.chain_set.create(tId=0)

            # change dates and status
            chain.status = True
            chain.end = int(timezone.now().timestamp())
            chain.start = 1
            chain.endDate = timestampToDate(chain.end)
            chain.save()
            # get number of attacks
            chainInfo = apiCall('faction', factionId, 'chain', key, sub='chain')
            if 'apiError' in chainInfo:
                print('[COMMAND live] api key error: {}'.format((chainInfo['apiError'])))
                break

            stopAfterNAttacks = chainInfo.get('current')
            print('[COMMAND live] stop after {} attacks'.format(stopAfterNAttacks))
            if stopAfterNAttacks:
                attacks = apiCallAttacks(factionId, chain.start, chain.end, key, stopAfterNAttacks=stopAfterNAttacks)
            else:
                attacks = dict({})

            # delete old report and create new
            chain.report_set.all().delete()
            report = chain.report_set.create()
            print('[COMMAND live] new report created')

            # refresh members
            members = apiCall('faction', factionId, 'basic', key, sub='members')
            if 'apiError' in members:
                print('[COMMAND live] api key error: {}'.format((members['apiError'])))
                break
            faction.member_set.all().delete()
            for m in members:
                faction.member_set.create(tId=m, name=members[m]['name'], lastAction=members[m]['last_action'], daysInFaction=members[m]['days_in_faction'])
            members = faction.member_set.all()

            fillReport(faction, members, chain, report, attacks, stopAfterNAttacks)

            print("[COMMAND live] end")
