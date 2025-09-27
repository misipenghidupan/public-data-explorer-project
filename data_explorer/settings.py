"""
Django Settings for Wikidata Explorer - Post-Architectural Refactor
**Target: Django 5.1.4, PyMongo 4.10.1**
"""
import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key
import logging.config
import sys
import time

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# --- Application definition ---
# Note: You must ensure 'corsheaders' is compatible with Django 5.1.4
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders', 
    'explorer',
]

# Note: You must ensure 'whitenoise.middleware.WhiteNoiseMiddleware' is correct for Django 5.1.4
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wikidata_explorer.urls'
WSGI_APPLICATION = 'wikidata_explorer.wsgi.application'

# --- DATABASE CONFIGURATION ---
# SQLite for Django ORM
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- MONGODB CONFIGURATION (PyMongo 4.x) ---
# Used by CacheManager
MONGODB_SETTINGS = {
    'CONNECTION_STRING': os.environ.get('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/'),
    'DATABASE_NAME': os.environ.get('MONGODB_DATABASE', 'wikidata_explorer'),
    'CACHE_COLLECTION': os.environ.get('MONGODB_CACHE_COLLECTION', 'sparql_cache'),
    'CACHE_TTL_SECONDS': int(os.environ.get('MONGODB_CACHE_TTL', '3600')),
    'CONNECTION_POOL': {
        'maxPoolSize': int(os.environ.get('MONGODB_MAX_POOL_SIZE', '50')),
        'serverSelectionTimeoutMS': int(os.environ.get('MONGODB_SERVER_TIMEOUT', '5000')),
        'connectTimeoutMS': int(os.environ.get('MONGODB_CONNECT_TIMEOUT', '10000')),
    },
    'RETRY_WRITES': os.environ.get('MONGODB_RETRY_WRITES', 'true').lower() == 'true',
    'RETRY_READS': os.environ.get('MONGODB_RETRY_READS', 'true').lower() == 'true',
}

# --- SPARQL SERVICE CONFIGURATION ---
SPARQL_SETTINGS = {
    'ENDPOINT_URL': os.environ.get('SPARQL_ENDPOINT', 'https://query.wikidata.org/sparql'),
    'TIMEOUT_SECONDS': int(os.environ.get('SPARQL_TIMEOUT', '20')),
}

# --- LOGGING CONFIGURATION ---
# (Using your full, detailed logging block)
LOGGING_CONFIG = None
LOGGING = { 
    'version': 1, 'disable_existing_loggers': False,
    'formatters': {
        'json': {'()': 'pythonjsonlogger.jsonlogger.JsonFormatter', 'format': '%(asctime)s %(name)s %(levelname)s %(message)s'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'json'},
        'file': {'class': 'logging.handlers.RotatingFileHandler', 'filename': BASE_DIR / 'logs' / 'wikidata_explorer.log', 'formatter': 'json'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'explorer': {'handlers': ['console', 'file'], 'level': 'DEBUG' if DEBUG else 'INFO', 'propagate': False},
        'pymongo': {'handlers': ['console', 'file'], 'level': 'WARNING', 'propagate': False},
    },
}
(BASE_DIR / 'logs').mkdir(exist_ok=True)
logging.config.dictConfig(LOGGING)

# --- DJANGO 5.1.4 SPECIFIC SETTINGS ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ... (rest of your Django 5.1.4 configuration, including TEMPLATES, STATICFILES, etc.)