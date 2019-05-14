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
        print("[command.chain.livereport] start")

        for faction in Faction.objects.all():
            print("[command.chain.livereport] faction {}".format(faction))

            # get api key
            if faction.apiString == "0":
                print("[command.chain.livereport] no api key found")
                continue
            factionId = faction.tId
            keyHolder, key = faction.get_random_key()
            print("[command.chain.livereport] using {} api key".format(keyHolder))

            # live chains
            liveChain = apiCall("faction", factionId, "chain", key, sub="chain")
            if 'apiError' in liveChain:
                print('[command.chain.livereport] api key error: {}'.format((liveChain['apiError'])))
                continue

            # if not bool(liveChain["current"]):
            if int(liveChain["current"]) < 10:
                print("[command.chain.livereport] no active chain")
                faction.chain_set.filter(tId=0).delete()
                print("[command.chain.livereport] report 0 deleted")
            else:
                # get chain
                print('[command.chain.livereport] this is a live report')
                chain = faction.chain_set.filter(tId=0).first()
                if chain is None:
                    print('[command.chain.livereport] create chain 0')
                    chain = faction.chain_set.create(tId=0)

                chain.status = True
                chain.end = int(timezone.now().timestamp())
                chain.start = int(liveChain.get("start"))
                chain.nHits = int(liveChain.get("current"))
                # chain.createReport = True
                chain.save()

                # delete old report and create new
                print('[command.chain.livereport] create big chain report: {}'.format(chain))
                report = chain.report_set.first()
                if report is None:
                    report = chain.report_set.create()
                    print('[command.chain.livereport] new report created')
                else:
                    print('[command.chain.livereport] report found')

                # get members (no refresh)
                # members = faction.member_set.all()

                # update members
                members = updateMembers(faction)
                if 'apiError' in members:
                    print("[command.chain.livereport] error in API continue to next chain: {}", members['apiError'])
                    continue

                attacks = apiCallAttacks(faction, chain)

                if "error" in attacks:
                    print("[command.chain.livereport] error apiCallAttacks: {}".format(attacks["error"]))
                else:
                    fillReport(faction, members, chain, report, attacks)

                chain.save()

                break  # do just one chain report / call

            print("[command.chain.livereport] end")
