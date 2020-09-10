import schedule
import time
import os


def every_minute():
    os.system('python manage.py chainreport2 1')
    os.system('python manage.py chainreport2 2')
    os.system('python manage.py chainreport2 3')
    os.system('python manage.py chainreport2 4')
    os.system('python manage.py chainreport2 5')
    os.system('python manage.py chainreport2 6')
    os.system('python manage.py chainreport2 7')
    os.system('python manage.py chainreport2 8')
    os.system('python manage.py chainreport2 9')
    os.system('python manage.py chainreport2 10')
    os.system('python manage.py chainreport2 11')

    os.system('python manage.py attacksreport2 1')
    os.system('python manage.py attacksreport2 2')
    os.system('python manage.py attacksreport2 3')
    os.system('python manage.py attacksreport2 4')
    os.system('python manage.py attacksreport2 5')
    os.system('python manage.py attacksreport2 6')
    os.system('python manage.py attacksreport2 7')
    os.system('python manage.py attacksreport2 8')
    os.system('python manage.py attacksreport2 9')
    os.system('python manage.py attacksreport2 10')

    os.system('python manage.py revivesreport 1')
    os.system('python manage.py revivesreport 2')
    os.system('python manage.py revivesreport 3')
    os.system('python manage.py revivesreport 4')
    os.system('python manage.py revivesreport 5')
    os.system('python manage.py revivesreport 6')
    os.system('python manage.py revivesreport 7')
    os.system('python manage.py revivesreport 8')
    os.system('python manage.py revivesreport 9')
    os.system('python manage.py revivesreport 10')


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


while True:
    schedule.run_pending()
    time.sleep(1)
