#!/bin/bash


for f in logs/2019/*; do
  name=$(echo "$f" | sed -n 's/.*\([0-9]\{4\}\-[0-9]\{2\}\-[0-9]\{2\}\).*/\1/p')
  echo "File -> $f -> $name"
    if test -f "../../yata/media/analytics/api-v1_$name.json"; then
        echo "api-v1_$name.json exists"
    else
        zcat $f | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/api-v1_$name.json -p goaccess_public.conf --date-spec=hr
    fi
    if test -f "../../yata/media/analytics/web_$name.json"; then
        echo "api-v1_$name.json exists"
    else
        zcat $f | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/web_$name.json -p goaccess_public.conf --date-spec=hr
    fi
done
