release: mkdir logs && touch logs/django.log && python src/manage.py migrate
web: cd src && gunicorn twitter_chatbot.wsgi
stream_listener: cd src && python manage.py shell < twitter_app/stream_listener.py
celery: cd src && celery -A tasks worker --loglevel=INFO
celery_beat: cd src && celery -A tasks beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler