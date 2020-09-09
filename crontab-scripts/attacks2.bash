#!/bin/bash

# command name
COM="attacksreport2"

# log file
LOG=~/logs/$COM-$1-$(date +%d-%m-%Y).log

source ~/venv/bin/activate

echo "START CRONTAB OF " $(date +%d-%m-%Y" "%H:%M:%S) >> $LOG
flock -n /tmp/$COM-$1.lock -c "python3 ~/yata/manage.py "$COM" "$1" >> $LOG 2>&1"
