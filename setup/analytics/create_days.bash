#!/bin/bash

# old loot
#cat ./logs/*.log | grep 'timings' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/old-loot_last-days.html -p goaccess_public.conf --date-spec=hr

# api v1
cat ./logs/*/*.log | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics/api-v1_last-days.html -p goaccess_public.conf --date-spec=hr

# web
cat ./logs/*/*.log | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | sed 's/bazaar\/update\/.*\sHTTP/bazaar\/update\/ HTTP/' | goaccess - -o ../../yata/media/analytics/web_last-days.html -p goaccess_public.conf --date-spec=hr
