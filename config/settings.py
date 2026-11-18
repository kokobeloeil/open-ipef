"""Configuration du site Prépa IPEF.

Toutes les valeurs sensibles sont lues dans les variables d'environnement
(voir .env.example).
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def _charger_env(fichier):
    """Charge un fichier .env simple (CLE=valeur) sans dépendance externe."""
    if not fichier.exists():
        return
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        os.environ.setdefault(cle.strip(), valeur.strip())


_charger_env(BASE_DIR / ".env")


def env_bool(nom, defaut=False):
    return os.environ.get(nom, str(defaut)).strip().lower() in ("1", "true", "yes", "on", "oui")


def env_liste(nom, defaut=""):
    return [v.strip() for v in os.environ.get(nom, defaut).split(",") if v.strip()]


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-a-remplacer")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_liste("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_liste("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts",
    "core",
    "ressources",
    "faq",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Stockage des fichiers -------------------------------------------------
# Les fichiers ne sont jamais servis directement : ils passent par la vue
# « telecharger » qui vérifie les droits d'accès.
USE_S3 = env_bool("USE_S3", False)

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

if USE_S3:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.environ.get("S3_ACCESS_KEY_ID"),
            "secret_key": os.environ.get("S3_SECRET_ACCESS_KEY"),
            "bucket_name": os.environ.get("S3_BUCKET_NAME"),
            "endpoint_url": os.environ.get("S3_ENDPOINT_URL") or None,
            "region_name": os.environ.get("S3_REGION_NAME") or None,
            "default_acl": None,  # bucket privé
            "querystring_auth": True,  # URLs signées temporaires
            "querystring_expire": 600,
            "file_overwrite": False,
            "location": "media",
        },
    }

# --- Authentification ------------------------------------------------------
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Paramètres propres au site -------------------------------------------
SITE_NAME = "Prépa IPEF"
CODE_EQUIPE = os.environ.get("IPEF_CODE_EQUIPE", "")
MAX_UPLOAD_MB = int(os.environ.get("IPEF_MAX_UPLOAD_MB", "25"))
EXTENSIONS_AUTORISEES = [
    "pdf", "doc", "docx", "odt", "ppt", "pptx", "odp", "xls", "xlsx", "ods",
    "txt", "md", "tex", "zip", "png", "jpg", "jpeg", "mp3", "mp4",
]
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# --- E-mails ---------------------------------------------------------------
if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ["EMAIL_HOST"]
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Prépa IPEF <noreply@localhost>")

# --- Sécurité en production ------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "SAMEORIGIN"  # nécessaire pour l'aperçu PDF intégré
else:
    X_FRAME_OPTIONS = "SAMEORIGIN"
