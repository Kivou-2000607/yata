#!/bin/bash

y=$(date "+%Y" -d "4 day ago")
rsync -azv --progress --delete-after $YATA_SSH_LOGIN@$YATA_SSH_URL:~/admin/logs/http/$y/ logs/$y

y2=$(date "+%Y")
if [ $y2 != $y ]; then
    rsync -azv --progress --delete-after $YATA_SSH_LOGIN@$YATA_SSH_URL:~/admin/logs/http/$y2/ logs/$y2
fi
