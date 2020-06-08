import os
from .settings_base import BASE_DIR, INSTALLED_APPS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bogazici_sut',
        'USER': 'bogazici_sut',
        'PASSWORD': '123456789',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


if os.environ.get('DJANGO_DEBUG') == 'True':
    # Hakan's Settings:
    INSTALLED_APPS += [
        'django_extensions',
    ]