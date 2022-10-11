import os

import dj_database_url

from .common import *

ALLOWED_HOSTS = ['*']
DEBUG = False
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")


if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ["SECRET_KEY"]

# db

MAX_CONN_AGE = 600

DATABASES = dict()

DATABASES["default"] = dj_database_url.config(
    conn_max_age=MAX_CONN_AGE, ssl_require=True
)

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
