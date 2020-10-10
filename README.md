[![GitHub release](https://img.shields.io/github/release/kivou-2000607/yata.svg?style=for-the-badge&color=%23447e9b&label=Release&logo=github)](https://github.com/Kivou-2000607/yata/releases)
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/kivou-2000607/yata/v1.9.svg?style=for-the-badge&color=%23447e9b&label=Commit%20since%20last%20release&logo=github)](https://github.com/Kivou-2000607/yata/commits/master)
[![Discord](https://img.shields.io/discord/581227228537421825?style=for-the-badge&color=%23447e9b&label=Join%20the%20discord&logo=discord&logoColor=FFF)](https://yata.alwaysdata.net/discord)

# YATA: Yet Another Torn App

Helper website for the text-based online RPG Torn City https://www.torn.com/
The website is hosted here: https://yata.alwaysdata.net/

# Local Setup Instructions



## Setup guide
    git clone https://github.com/Kivou-2000607/yata.git

    cd yata

    pip install -r requirements.txt

Create a local .env file

    ###### REQUIRED ######
    DEBUG=True
    SECRET_KEY="super_secret_key"
    ALLOWED_HOSTS="*"

    # Database selection
    DATABASE=sqlite
    #DATABASE=postgresql
    #PG_NAME=yata
    #PG_USER=username
    #PG_PASSWORD=password
    #PG_HOST=localhost
    #PG_PORT=5432

    # REDIS
    #USE_REDIS=True
    #REDIS_HOST="redis://178.62.1.116:6379/1"
    #REDIS_PASSWORD="***"


    ###### OPTIONAL ######
    # Your TORN API KEY
    APIKEY="API KEY HERE" 
    # For most leaving this as default should be fine, but if you have any issues with -4 cache responses you may wish to increase this gradually
    CACHE_RESPONSE=10 

    # The amount of chain report crontabs to run when running crons manually via python dev_cron.py
    CHAIN_REPORT = 1

    # The amount of attack report crontabs to run when running crons manually via python dev_cron.py
    ATTACK_REPORT = 1

    # The amount of revive report crontabs to run when running crons manually via python dev_cron.py
    REVIVE_REPORT = 1

Then run setup.py to initalise everything

    python setup.py



## Running YATA

To emulate cron activity _dev_cron.py_ can be run as a seperate process. Cron jobs designed to run on a per minute basis will be run as such. Cron's with a longer delay will run on a 30 minute schedule.

    python dev_cron.py

To launch the application simple start the Django Application

    python manage.py runserver

The admin interface can be accessed via

    http://127.0.0.1:8000/admin
    Username: admin
    Password: adminpass

### Bazaar Default Items

By default the most commonly traded items are set to appear in https://yata.alwaysdata.net/bazaar/default/. This list can be adjusted.

    1. Logon To the Admin Section
    2. Go to the Items table
    3. Select the item you wish to add
    4. Enable the flag "OnMarket"
    5. Save
