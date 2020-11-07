#!/bin/bash

#zcat logs/2019/http-$1-$2-*.gz | goaccess -o perso/report-$1-$2.html -p goaccess_wip.conf
#cat logs/2020/http-*.log | goaccess -o perso/report-last-days.html -p goaccess_wip.conf --date-spec=hr

#zcat logs/2020/http-$1-$2-*.gz | grep "/loot/timings" | goaccess -o perso/report-$1-$2.html -p goaccess_wip.conf
#zcat logs/2020/http-$1-$2-$3.log.gz | grep "/loot/timings" | goaccess -o perso/report-$1-$2-$3.html -p goaccess_wip.conf
# cat logs/2020/http-*.log | grep "/loot/timings" | goaccess -o perso/report-loot.html -p goaccess_wip.conf --date-spec=hr
# cat logs/2020/http-*.log | grep "/bazaar/abroad/export" | goaccess -o perso/report-stocks.html -p goaccess_wip.conf --date-spec=hr
# cat logs/2020/http-*.log | goaccess -o perso/report.html -p goaccess_wip.conf --date-spec=hr


#find ./logs2 -name *.log -print0 | xargs -0 cat | sed  '/static\|loot\/timings/d' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o perso/report-noloot.html -p goaccess_wip.conf --date-spec=hr
#find ./logs2 -name *.log -print0 | xargs -0 cat | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o perso/report-all.html -p goaccess_wip.conf --date-spec=hr
find ./logs -name *.log -print0 | xargs -0 cat | grep 'timings' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o perso/report-onlyloot.html -p goaccess_wip.conf --date-spec=hr
