"""Configuración aislada para verificar el módulo, sin usar la base ni secretos reales."""
import os
os.environ.setdefault('SECRET_KEY', 'solo-pruebas-dendrometro-no-produccion')
from core.settings import *  # noqa

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
MIDDLEWARE = [m for m in MIDDLEWARE if 'preventconcurrentlogins' not in m and 'UpdateLastActivityMiddleware' not in m]
