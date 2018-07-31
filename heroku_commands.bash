heroku run:detached python manage.py migrate
heroku run:detached bash setupdb.bash --app torn-yata
heroku run:detached python manage.py collectstatics --app torn-yata
heroku logs --app torn-yata --tail
git push heroku master
