import os
from .settings_base import BASE_DIR, ALLOWED_HOSTS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bogazici_sut',
        'USER': 'bogazici_sut',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}
ALLOWED_HOSTS = ['localhost']

