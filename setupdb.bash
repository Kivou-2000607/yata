# set up database
rm -frv db.sqlite3
python manage.py migrate
python manage.py makemigrations
python manage.py migrate
#python manage.py createsuperuser
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')"
