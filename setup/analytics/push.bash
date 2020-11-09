#!/bin/bash

rsync -azv --delete-after ../../yata/media/analytics/ $YATA_SSH_LOGIN@$YATA_SSH_URL:/home/yata/yata/yata/media/analytics/

source $YATA_VENV
../../manage.py send_analytics
