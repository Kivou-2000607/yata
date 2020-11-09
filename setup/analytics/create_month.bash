#!/bin/bash

# old loot
find ./logs/$1 -name http-$1-$2-*.log.gz -print0 | xargs -0 zcat | grep 'timings' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics//old-loot_$1-$2 -p goaccess_public.conf 

# api v1 
find ./logs/$1 -name http-$1-$2-*.log.gz -print0 | xargs -0 zcat | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics/api-v1_$1-$2.html -p goaccess_public.conf

# web
zcat ./logs/$1/http-$1-$2-*.log.gz | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | sed 's/bazaar\/update\/.*\sHTTP/bazaar\/update\/ HTTP/' | goaccess - -o ../../yata/media/analytics/web_$1-$2.html -p goaccess_public.conf
