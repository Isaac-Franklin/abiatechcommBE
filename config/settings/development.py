from .base import *

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [  # Fixed typo: CLAASS -> CLASSES
        'rest_framework.permissions.IsAuthenticated',  # Require authentication by default
    ],
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'abiatechcomm',
    'DESCRIPTION': 'Abia Tech Communication Backend ',
    'VERSION': '1.0.0',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost",
    "https://winxnovel.netlify.app", 
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "https://winxnovel.netlify.app", 
]


CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]


SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"',
        },
    },
}

import os
# SECRET_KEY = os.getenv("SECRET_KEY")

