#!/bin/bash

# old loot
find ./logs -name "*.log" -print0 | xargs -0 cat | grep 'timings' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/old-loot_last-days.html -p goaccess_public.conf --date-spec=hr
find ./logs -name "*.log" -print0 | xargs -0 cat | grep 'timings' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/old-loot_last-days.json -p goaccess_public.conf --date-spec=hr

# api v1
find ./logs -name "*.log" -print0 | xargs -0 cat | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/api-v1_last-days.html -p goaccess_public.conf --date-spec=hr
find ./logs -name "*.log" -print0 | xargs -0 cat | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/api-v1_last-days.json -p goaccess_public.conf --date-spec=hr

# web
find ./logs -name "*.log" -print0 | xargs -0 cat | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | sed 's/bazaar\/update\/.*\sHTTP/bazaar\/update\/ HTTP/' | goaccess -o ../../yata/media/analytics/web_last-days.html -p goaccess_public.conf --date-spec=hr
find ./logs -name "*.log" -print0 | xargs -0 cat | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | sed 's/bazaar\/update\/.*\sHTTP/bazaar\/update\/ HTTP/' | goaccess -o ../../yata/media/analytics/web_last-days.json -p goaccess_public.conf --date-spec=hr
