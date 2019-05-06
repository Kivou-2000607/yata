from django.core.management.base import BaseCommand
from django.utils import timezone

from chain.models import Faction
from yata.handy import timestampToDate

from chain.functions import apiCallAttacks
from chain.functions import apiCall
from chain.functions import fillReport
from chain.functions import updateMembers


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND updatechains] start")

        for faction in Faction.objects.all():
            print("[COMMAND updatechains] faction {}".format(faction))

            # get api key
            if faction.apiString == "0":
                print("[COMMAND updatechains] no api key found")
                continue
            factionId = faction.tId
            keyHolder, key = faction.get_random_key()

            # # live chains
            # liveChain = apiCall("faction", factionId, "chain", key, sub="chain")
            # if 'apiError' in liveChain:
            #     print('[COMMAND updatechains] api key error: {}'.format((liveChain['apiError'])))
            #     continue
            #
            # if not bool(liveChain["current"]):
            #     print("[COMMAND updatechains] no active chain")
            #     faction.chain_set.filter(tId=0).delete()
            #     print("[COMMAND updatechains] report 0 deleted")
            # else:
            #     # get chain
            #     print('[COMMAND updatechains] this is a live report')
            #     chain = faction.chain_set.filter(tId=0).first()
            #     if chain is None:
            #         print('[COMMAND updatechains] create chain 0')
            #         chain = faction.chain_set.create(tId=0)
            #
            #     chain.status = True
            #     chain.end = int(timezone.now().timestamp())
            #     chain.endDate = timestampToDate(chain.end)
            #     chain.start = int(liveChain.get("start"))
            #     chain.nHits = int(liveChain.get("current"))
            #     # chain.createReport = True
            #     chain.save()


            # get all chain
            print('[COMMAND updatechains] get big chains')
            chains = faction.chain_set.filter(createReport=True).all()
            for chain in chains:
                # delete old report and create new
                print('[COMMAND updatechains] create big chain report: {}'.format(chain))
                report = chain.report_set.first()
                if report is None:
                    report = chain.report_set.create()
                    print('[COMMAND updatechains] new report created')
                else:
                    print('[COMMAND updatechains] report found')

                # get members (no refresh)
                # members = faction.member_set.all()

                # update members
                members = updateMembers(faction)
                if 'apiError' in members:
                    print("[COMMAND updatechains] error in API continue to next chain: {}", members['apiError'])
                    continue

                attacks = apiCallAttacks(faction, chain)

                if "error" in attacks:
                    print("[COMMAND updatechains] error apiCallAttacks: {}".format(attacks["error"]))
                else:
                    _, _, _, finished = fillReport(faction, members, chain, report, attacks)
                    print("[COMMAND updatechains] report finished: {}".format(finished))
                    chain.createReport = not finished

                chain.save()

                break  # do just one chain report / call

            print("[COMMAND updatechains] end")
