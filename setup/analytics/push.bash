#!/bin/bash

rsync -azv --delete-after ../../yata/media/analytics/*.html $YATA_SSH_LOGIN@$YATA_SSH_URL:/home/yata/yata/yata/media/analytics/
rsync -azv --delete-after ../../yata/media/analytics/*.html kivou@178.128.32.61:/home/kivou/yata/yata/media/analytics/

source $YATA_VENV
../../manage.py analytics
