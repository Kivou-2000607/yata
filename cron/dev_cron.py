import schedule
import time
import os
from decouple import config


def every_minute():
    for x in range(1, int(config("CHAIN_REPORT")) + 1):
        print("Running Chain Report: " + str(x))
        os.system('python manage.py chain ' + str(x))

    for x in range(1, int(config("ATTACK_REPORT")) + 1):
        print("Running Attack Report: " + str(x))
        os.system('python manage.py attacks ' + str(x))

    for x in range(1, int(config("REVIVE_REPORT")) + 1):
        print("Running Revive Report: " + str(x))
        os.system('python manage.py revives ' + str(x))


def every_30_minutes():
    os.system('python manage.py loot')
    os.system('python manage.py stocks')
    os.system('python manage.py check_keys')
    os.system('python manage.py items')
    os.system('python manage.py factions')
    os.system('python manage.py awards')
    os.system('python manage.py territories')
    os.system('python manage.py companies')


print("Emulating cron jobs. Hourly or daily scripts will run on a 30 minute basis for debugging")

schedule.every(1).minutes.do(every_minute)
schedule.every(30).minutes.do(every_30_minutes)

every_minute()
every_30_minutes()

while True:
    schedule.run_pending()
    time.sleep(1)
