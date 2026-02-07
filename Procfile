# Procfile for Heroku/Railway/Render deployment
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 'app:create_app()'
worker: python -m celery -A celery_app worker --loglevel=info
