from pathlib import Path

# import datetime as dt
import os

import environ


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

# Busca siempre el archivo .env en la raíz del proyecto.
ENV_FILE = BASE_DIR / ".env"
environ.Env.read_env(ENV_FILE)

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[],
)

# PythonAnywhere entrega HTTPS mediante su proxy inverso.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

# Cookies solo por HTTPS.
SECURE_SSL_REDIRECT = env.bool(
    "SECURE_SSL_REDIRECT",
    default=True,
)

SESSION_COOKIE_SECURE = env.bool(
    "SESSION_COOKIE_SECURE",
    default=True,
)

CSRF_COOKIE_SECURE = env.bool(
    "CSRF_COOKIE_SECURE",
    default=True,
)

# HSTS: inicialmente 1 hora para comprobar que todo funcione.
SECURE_HSTS_SECONDS = env.int(
    "SECURE_HSTS_SECONDS",
    default=3600,
)

# No los actives aún hasta confirmar que todos los subdominios usan HTTPS.
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False


# Application definition

DEFAULT_DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

LOCAL_APPS = [
    "homeApp",
    "UsuarioApp",
    "ProyectosApp",
    "EspaciosApp",
    "DendometroApp",
]

THIRD_APPS = [
    "tailwind",
    "theme",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "crispy_forms",
    "crispy_tailwind",
    "preventconcurrentlogins",
    # "axes",  # Desactivado temporalmente
]


INSTALLED_APPS = DEFAULT_DJANGO_APPS + LOCAL_APPS + THIRD_APPS


TAILWIND_APP_NAME = "theme"

INTERNAL_IPS = env.list("INTERNAL_IPS", default=[])

NPM_BIN_PATH = env("NPM_BIN_PATH", default="")

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

CRISPY_TEMPLATE_PACK = "tailwind"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware",
    # "axes.middleware.AxesMiddleware",  # Desactivado temporalmente
    "homeApp.middleware.UpdateLastActivityMiddleware",
]


ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # "axes.backends.AxesStandaloneBackend",  # Desactivado temporalmente
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

WSGI_APPLICATION = "core.wsgi.application"

MFA_ADAPTER = "allauth.mfa.adapter.DefaultMFAAdapter"

MFA_FORMS = {
    "authenticate": "allauth.mfa.forms.AuthenticateForm",
    "reauthenticate": "allauth.mfa.forms.AuthenticateForm",
    "activate_totp": "allauth.mfa.forms.ActivateTOTPForm",
    "deactivate_totp": "allauth.mfa.forms.DeactivateTOTPForm",
}

SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 10,
        },
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "es-cl"

TIME_ZONE = "America/Santiago"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Correo:
# Se mantiene en consola porque aún no hay proveedor SMTP.
# No afecta el registro ya que ACCOUNT_EMAIL_VERIFICATION = "none".
# if DEBUG:
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# else: EMAIL_BACKEND = [Configuración de correo]


ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
LOGIN_REDIRECT_URL = "Home"
LOGIN_URL = "account_login"

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

# No se solicita confirmación porque no existe sistema de correos.
ACCOUNT_EMAIL_VERIFICATION = "none"  # none, optional, mandatory

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/login/"
ACCOUNT_ADAPTER = "UsuarioApp.adapters.NoSignupAccountAdapter"

SESSION_COOKIE_AGE = 1800  # 30 minutos


# MFA

MFA_RECOVERY_CODE_COUNT = 10
# El número de códigos de recuperación.

MFA_TOTP_PERIOD = 30
# El período durante el cual un código TOTP será válido, en segundos.

MFA_TOTP_DIGITS = 6
# The number of digits for TOTP codes.

# django-axes: protección frente a intentos de acceso repetidos

# delta = dt.timedelta(minutes=5)

# AXES_FAILURE_LIMIT = 3
# AXES_COOLOFF_TIME = delta
# AXES_RESET_ON_SUCCESS = True  # restablecerá el número de inicios de sesión fallidos
# AXES_ENABLE_ACCESS_FAILURE_LOG = True
# AXES_LOCK_OUT_AT_FAILURE = True  # bloquea al usuario

# ------------------------------------------
if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }
