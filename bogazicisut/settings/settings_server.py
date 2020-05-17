import os
from .settings_base import BASE_DIR, ALLOWED_HOSTS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bogazici_sut',
        'USER': 'bogazici_sut',
        'PASSWORD': '123456789',
        'HOST': '127.0.0.1',
        'PORT': '5433',
    }
}
ALLOWED_HOSTS = ['localhost']

