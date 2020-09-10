[![GitHub release](https://img.shields.io/github/release/kivou-2000607/yata.svg?style=for-the-badge&color=%23447e9b&label=Release&logo=github)](https://github.com/Kivou-2000607/yata/releases)
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/kivou-2000607/yata/v1.9.svg?style=for-the-badge&color=%23447e9b&label=Commit%20since%20last%20release&logo=github)](https://github.com/Kivou-2000607/yata/commits/master)
[![Discord](https://img.shields.io/discord/581227228537421825?style=for-the-badge&color=%23447e9b&label=Join%20the%20discord&logo=discord&logoColor=FFF)](https://yata.alwaysdata.net/discord)

# YATA: Yet Another Torn App

Helper website for the text-based online RPG Torn City https://www.torn.com/
The website is hosted here: https://yata.alwaysdata.net/

# Local Setup Instructions



## Setup
    git clone https://github.com/Kivou-2000607/yata.git

    cd yata

    pip install -r requirements.txt

Create a local .env file

    SECRET_KEY="SUPER_SECRET_KEY"
    CACHE_RESPONSE=10
    
Setup your Torn API key in setup.py. Then run setup.py to initalise everything

    python setup.py



## Running YATA

To emulate cron activity _dev_cron.py_ can be run as a seperate process. Cron jobs designed to run on a per minute basis will be run as such. Cron's with a longer delay will run on a 30 minute schedule.

    python dev_cron.py

To launch the application simple start the Django Application

    python manage.py runserver