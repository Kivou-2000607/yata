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
            chainInfo = apiCall('faction', factionId, 'chain', key, sub='chain')
            if 'apiError' in chainInfo:
                print('[COMMAND live] api key error: {}'.format((chainInfo['apiError'])))
                break
            chain.status = True
            chain.end = int(timezone.now().timestamp())
            chain.endDate = timestampToDate(chain.end)
            chain.start = int(chainInfo.get("start"))
            chain.startDate = timestampToDate(chain.start)
            chain.save()

            attacks = apiCallAttacks(factionId, chain.start, chain.end, key)

            # delete old report and create new
            chain.report_set.all().delete()
            report = chain.report_set.create()
            print('[COMMAND live] new report created')

            # call members
            members = apiCall('faction', factionId, 'basic', key, sub='members')
            if 'apiError' in members:
                print('[COMMAND live] api key error: {}'.format((members['apiError'])))
                break

            # update members
            membersDB = faction.member_set.all()
            for m in members:
                memberDB = membersDB.filter(tId=m).first()
                if memberDB is not None:
                    print('[VIEW members] member {} updated'.format(members[m]['name']))
                    memberDB.name = members[m]['name']
                    memberDB.lastAction = members[m]['last_action']
                    memberDB.daysInFaction = members[m]['days_in_faction']
                    memberDB.save()
                else:
                    print('[VIEW members] member {} created'.format(members[m]['name']))
                    faction.member_set.create(tId=m, name=members[m]['name'], lastAction=members[m]['last_action'], daysInFaction=members[m]['days_in_faction'])

            fillReport(faction, membersDB, chain, report, attacks)

            print("[COMMAND live] end")
