"""
Django settings for AURA project.

MISIÓN 1 — Cambios aplicados:
  [T2] DB_NAME, DB_USER y ALLOWED_HOSTS ahora vienen del .env
  [T3] DEBUG por defecto es False; solo es True si el .env lo declara explícitamente
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Cargar variables de entorno ───────────────────────────────────────────────
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ── Seguridad ─────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv('SECRET_KEY')

# [T3] CAMBIO: el default ahora es 'False'.
# En desarrollo, ponés DEBUG=True en tu .env y listo.
# Si el .env no existe o la variable no está, el servidor arranca en modo seguro.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# [T2] CAMBIO: ALLOWED_HOSTS viene del .env como lista separada por comas.
# Ejemplo en .env de desarrollo: ALLOWED_HOSTS=127.0.0.1,localhost
# Ejemplo en .env de producción: ALLOWED_HOSTS=tudominio.com,www.tudominio.com
_allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]


# ── Aplicaciones instaladas ───────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web_ujap',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ── Base de Datos (PostgreSQL) ────────────────────────────────────────────────
# [T2] CAMBIO: DB_NAME y DB_USER ahora vienen del .env también.
# Antes estaban hardcodeados como 'db_ujap' y 'postgres'.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.getenv('DB_NAME', 'db_ujap'),      # antes: 'db_ujap' fijo
        'USER':     os.getenv('DB_USER', 'postgres'),     # antes: 'postgres' fijo
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST':     os.getenv('DB_HOST', '127.0.0.1'),
        'PORT':     os.getenv('DB_PORT', '5432'),
    }
}


# ── Validación de contraseñas ─────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── Internacionalización ──────────────────────────────────────────────────────

LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True


# ── Archivos Estáticos ────────────────────────────────────────────────────────

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# ── Email y Auth ──────────────────────────────────────────────────────────────

SITE_NAME = "UJAP.online"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL  = os.getenv('DEFAULT_FROM_EMAIL')

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/pagina/'
AUTH_USER_MODEL = 'web_ujap.Usuario'