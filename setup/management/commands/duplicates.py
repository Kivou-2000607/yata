"""
Copyright 2021 kivou@yata.yt

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""

from django.core.management.base import BaseCommand

from faction.models import RevivesReport
from faction.models import AttacksReport
from yata.handy import logdate

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-r', '--revives', action='store_true')
        parser.add_argument('-a', '--attacks', action='store_true')

    def handle(self, **options):

        #
        # REVIVES
        #

        if options.get("revives", False):

            print(f"[CRON {logdate()}] start looking for duplicates in revives")

            # loop over reports
            for report in RevivesReport.objects.all():
                print(f"[CRON {logdate()}] {report}")

                # find duplicates

                # get all objs of the report
                objs = report.revive_set.all()
                # init tid lists to check for duplicates and store them
                objs_tid_all = []
                objs_tid_duplicates = []
                # loop over objs
                for obj in objs:
                    # check if objs tId already registered
                    if obj.tId in objs_tid_all:
                        print(f"[CRON {logdate()}] found duplicate obj tid = {obj.tId}")
                        # append in duplicate list
                        objs_tid_duplicates.append(obj.tId)
                    else:
                        objs_tid_all.append(obj.tId)


                # delete duplicates

                # loop over the duplicated tId
                for i, obj_tid in enumerate(objs_tid_duplicates):
                    print(f"[CRON {logdate()}] {i}/{len(objs_tid_duplicates)} deletes tid = {obj_tid}")
                    # get all duplicated objects
                    objs_duplicates = objs.filter(tId=obj_tid)
                    # get first one (to keep it)
                    first_obj = objs_duplicates.first()
                    # delete the others
                    objs_to_delete = objs_duplicates.exclude(id=first_obj.id)
                    objs_to_delete.delete()


                # recompute report if duplicated data found

                # check if needs to be recomputed
                if len(objs_tid_duplicates):
                    report.fillReport()

        #
        # ATTACKS
        #

        if options.get("attacks", False):

            print(f"[CRON {logdate()}] start looking for duplicates in attacks")

            # loop over reports
            for report in AttacksReport.objects.all():
                print(f"[CRON {logdate()}] {report}")

                # find duplicates

                # get all objs of the report
                objs = report.attackreport_set.all()
                # init tid lists to check for duplicates and store them
                objs_tid_all = []
                objs_tid_duplicates = []
                # loop over objs
                for obj in objs:
                    # check if objs tId already registered
                    if obj.tId in objs_tid_all:
                        print(f"[CRON {logdate()}] found duplicate obj tid = {obj.tId}")
                        # append in duplicate list
                        objs_tid_duplicates.append(obj.tId)
                    else:
                        objs_tid_all.append(obj.tId)


                # delete duplicates

                # loop over the duplicated tId
                for i, obj_tid in enumerate(objs_tid_duplicates):
                    print(f"[CRON {logdate()}] {i}/{len(objs_tid_duplicates)} deletes tid = {obj_tid}")
                    # get all duplicated objects
                    objs_duplicates = objs.filter(tId=obj_tid)
                    # get first one (to keep it)
                    first_obj = objs_duplicates.first()
                    # delete the others
                    objs_to_delete = objs_duplicates.exclude(id=first_obj.id)
                    objs_to_delete.delete()


                # recompute report if duplicated data found

                # check if needs to be recomputed
                if len(objs_tid_duplicates):
                    report.fillReport()

            print(f"[CRON {logdate()}] end looking for duplicates in attacks")
