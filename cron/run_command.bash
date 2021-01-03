#!/bin/bash

# YATA root directory
YATA_DIR=~/yata

# virtualenv root directory
VENV_DIR=~/.virtualenvs/yata/

# log file
if [ "$2" == "" ]; then
  LOG_DIR=$YATA_DIR/cron/logs/$(date -u +%Y-%m)/$1
  LOG_FILE=$LOG_DIR/$1_$(date -u +%Y-%m-%d).log
else
  LOG_DIR=$YATA_DIR/cron/logs/$(date -u +%Y-%m)/$1-$2
  LOG_FILE=$LOG_DIR/$1-$2_$(date -u +%Y-%m-%d).log
fi

# create log directory
mkdir -p $LOG_DIR

# echo
echo "[BASH $(date -u "+%Y-%m-%d %T")] START" >> $LOG_FILE 2>&1
echo "[BASH $(date -u "+%Y-%m-%d %T")] Log file: $LOG_FILE" >> $LOG_FILE 2>&1

# sleep if report
if [[ "$1" == "chain" || "$1" == "attacks" || "$1" == "revives" ]]; then
  echo "[BASH $(date -u "+%Y-%m-%d %T")] Sleep for $2 seconds" >> $LOG_FILE 2>&1
  sleep $2
fi

# lock file
if [ "$2" == "" ]; then
  LOCK_FILE="/tmp/$1.lock"
else
  LOCK_FILE="/tmp/$1-$2.lock"
fi

# run command
source $VENV_DIR/bin/activate
flock -n $LOCK_FILE -c "python $YATA_DIR/manage.py $1 $2" >> $LOG_FILE 2>&1
# flock -n $LOCK_FILE -c "python $YATA_DIR/manage.py $1 $2"

echo "[BASH $(date -u "+%Y-%m-%d %T")] END" >> $LOG_FILE 2>&1
echo "" >> $LOG_FILE 2>&1
