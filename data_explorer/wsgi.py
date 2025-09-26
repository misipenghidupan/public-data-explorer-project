import os

from django.core.wsgi import get_wsgi_application

# This line MUST be 'data_explorer.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_explorer.settings')

application = get_wsgi_application()