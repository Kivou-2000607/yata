#!/bin/bash

# command name
COM="attacksBreakdown"

# log file
LOG=~/logs/$COM-$(date +%d-%m-%Y).log

source ~/venv/bin/activate

echo "START CRONTAB OF " $(date +%d-%m-%Y" "%H:%M:%S) >> $LOG
flock -n /tmp/$COM.lock -c "python3 ~/yata/manage.py "$COM" >> $LOG 2>&1"
