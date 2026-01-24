import os
import dj_database_url
from .base import *
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

DEBUG =False

STATIC_URL ="/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
  
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["nwoemma.pythonanywhere.com"]  # tighten later
