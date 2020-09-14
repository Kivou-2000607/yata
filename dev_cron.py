import schedule
import time
import os
from decouple import config


def every_minute():
    for x in range(1, int(config("CHAIN_REPORT")) + 1):
        print("Running Chain Report: " + str(x))
        os.system('python manage.py chainreport2 ' + str(x))

    for x in range(1, int(config("ATTACK_REPORT")) + 1):
        print("Running Attack Report: " + str(x))
        os.system('python manage.py attacksreport2 ' + str(x))

    for x in range(1, int(config("REVIVE_REPORT")) + 1):
        print("Running Revive Report: " + str(x))
        os.system('python manage.py revivesreport ' + str(x))


def every_30_minutes():
    os.system('python manage.py updateLoot')
    os.system('python manage.py updateStocks')
    os.system('python manage.py checkKeys')
    os.system('python manage.py updateItems')
    os.system('python manage.py updateFactions')
    os.system('python manage.py updateAwards')
    os.system('python manage.py updateTerritories')


print("Emulating cron jobs. Hourly or daily scripts will run on a 30 minute basis for debugging")

schedule.every(1).minutes.do(every_minute)
schedule.every(30).minutes.do(every_30_minutes)

every_minute()

while True:
    schedule.run_pending()
    time.sleep(1)
