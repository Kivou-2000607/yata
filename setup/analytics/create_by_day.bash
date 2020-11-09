#!/bin/bash

    
y=$(date "+%Y" -d "4 day ago")
t=$(date "+%Y-%m" -d "4 day ago")
echo $y
echo $t

for f in logs/$y/http-$t-*.log.gz; do
    name=$(echo "$f" | sed -n 's/.*\([0-9]\{4\}\-[0-9]\{2\}\-[0-9]\{2\}\).*/\1/p')
    echo "File -> $f -> $name"
    if test -f "../../yata/media/analytics/api-v1_$name.json"; then
        echo "api-v1_$name.json exists"
    else
	echo "api-v1_$name.json create"
        zcat $f | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/api-v1_$name.json -p goaccess_public.conf --date-spec=hr --no-progress
    fi
    if test -f "../../yata/media/analytics/web_$name.json"; then
        echo "web-v1_$name.json exists"
    else
	echo "web-v1_$name.json create"
        zcat $f | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/web_$name.json -p goaccess_public.conf --date-spec=hr --no-progress
    fi
done

for f in logs/$y/http-$t-*.log; do
    name=$(echo "$f" | sed -n 's/.*\([0-9]\{4\}\-[0-9]\{2\}\-[0-9]\{2\}\).*/\1/p')
    echo "File -> $f -> $name"
    if test -f "../../yata/media/analytics/api-v1_$name.json"; then
        echo "api-v1_$name.json exists"
    else
	echo "api-v1_$name.json create"
        cat $f | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/api-v1_$name.json -p goaccess_public.conf --date-spec=hr --no-progress
    fi
    if test -f "../../yata/media/analytics/web_$name.json"; then
        echo "web-v1_$name.json exists"
    else
	echo "web-v1_$name.json create"
        cat $f | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/web_$name.json -p goaccess_public.conf --date-spec=hr --no-progress
    fi
done


y2=$(date "+%Y")
t2=$(date "+%Y-%m")
echo $y2
echo $t2
if [ $t2 != $t ]; then
    for f in logs/$y2/http-$t2-*.log.gz; do
	name=$(echo "$f" | sed -n 's/.*\([0-9]\{4\}\-[0-9]\{2\}\-[0-9]\{2\}\).*/\1/p')
	echo "File -> $f -> $name"
	if test -f "../../yata/media/analytics/api-v1_$name.json"; then
            echo "api-v1_$name.json exists"
	else
	    echo "api-v1_$name.json create"
            zcat $f | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/api-v1_$name.json -p goaccess_public.conf --date-spec=hr --no-progress
	fi
	if test -f "../../yata/media/analytics/web_$name.json"; then
            echo "web-v1_$name.json exists"
	else
	    echo "web-v1_$name.json create"
            zcat $f | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/web_$name.json -p goaccess_public.conf --date-spec=hr --no-progress
	fi
    done

    for f in logs/$y2/http-$t2-*.log; do
	name=$(echo "$f" | sed -n 's/.*\([0-9]\{4\}\-[0-9]\{2\}\-[0-9]\{2\}\).*/\1/p')
	echo "File -> $f -> $name"
	if test -f "../../yata/media/analytics/api-v1_$name.json"; then
            echo "api-v1_$name.json exists"
	else
	    echo "api-v1_$name.json create"
            cat $f | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/api-v1_$name.json -p goaccess_public.conf --date-spec=hr --no-progress
	fi
	if test -f "../../yata/media/analytics/web_$name.json"; then
            echo "web-v1_$name.json exists"
	else
	    echo "web-v1_$name.json create"
            cat $f | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | goaccess -o ../../yata/media/analytics/web_$name.json -p goaccess_public.conf --date-spec=hr --no-progress
	fi
    done
fi
