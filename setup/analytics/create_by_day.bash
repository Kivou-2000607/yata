#!/bin/bash

# get today
y=$(date "+%Y")
m=$(date "+%m")
d=$(date "+%d")

yp=$(date "+%Y" -d "4 days ago")
mp=$(date "+%m" -d "4 days ago")
dp=$(date "+%d" -d "4 days ago")

# remove todays log
sections=("api-v1 web")
for section in $sections; do
    rm -vf $file "../../yata/media/analytics/${section}_$y-$m-$d."*
    rm -vf $file ../../yata/media/analytics/${section}_$y-$m-$(date "+%d" -d "1 days ago").*
done

# check if needs to loop over last month/year directory
if [[ "$m" == "$mp" ]] && [[ "$y" == "$yp" ]]; then
    heads=("logs/$y/http-$y-$m-")
else
    heads=("logs/$y/http-$y-$m- logs/$yp/http-$yp-$mp-")
fi

# loop over the folders
for head in $heads; do
    echo "head" $head

    # loop of the logs
    for f in $head*; do
	name=$(echo "$f" | sed -n 's/.*\([0-9]\{4\}\-[0-9]\{2\}\-[0-9]\{2\}\).*/\1/p')
	echo "file" $f

	# check if api json file is missing to create the report
	if [ ! -f ../../yata/media/analytics/api-v1_$name.json ]; then
	    echo "api-v1_$name.json create"

	    # check .log.gz or .log
	    if [[ "$f" == *.gz ]]; then
		zcat $f | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics/api-v1_$name.json -p ./goaccess_public.conf --date-spec=hr
	    else
		#cat $f | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/'
		cat $f | grep '/api/v1/' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics/api-v1_$name.json -p ./goaccess_public.conf --date-spec=hr
	    fi
	fi

	# check if web json file is missing to create the report
	if [ ! -f ../../yata/media/analytics/web_$name.json ]; then
	    echo "web_$name.json create"

	    # check .log.gz or .log
	    if [[ "$f" == *.gz ]]; then
		zcat $f | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics/web_$name.json -p goaccess_public.conf --date-spec=hr
	    else
		cat $f | sed '/static\|loot\/timings\|abroad\/export\|abroad\/import\|targets\/import\|targets\/export\|\/api\|\/share/d' | sed 's/?.*\sHTTP/ HTTP/' | goaccess - -o ../../yata/media/analytics/web_$name.json -p goaccess_public.conf --date-spec=hr
	    fi
	fi

    done
done
