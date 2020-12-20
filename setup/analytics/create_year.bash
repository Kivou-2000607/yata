#!/bin/bash

echo "CREATE YEAR" $1

# old loot
zcat ./logs/$1/http-$1-*.log.gz | grep 'timings' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics/old-loot_$1.html -p goaccess_public.conf 

# api v1 
zcat ./logs/$1/http-$1-*.log.gz | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics/api-v1_$1.html -p goaccess_public.conf

# web
zcat ./logs/$1/http-$1-*.log.gz | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | sed 's/bazaar\/update\/.*\sHTTP/bazaar\/update\/ HTTP/' | goaccess - -o ../../yata/media/analytics/web_$1.html -p goaccess_public.conf
