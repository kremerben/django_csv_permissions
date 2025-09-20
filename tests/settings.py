import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "test-secret-key"
DEBUG = True
USE_TZ = True
TIME_ZONE = "UTC"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "testdb.sqlite3"),
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django_csv_permissions",
    "tests.sampleapp",
]

MIDDLEWARE = []
ROOT_URLCONF = "tests.urls"
ALLOWED_HOSTS = ["*"]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Disable migrations for sampleapp to speed up tests; allow syncdb-style creation
MIGRATION_MODULES = {"tests.sampleapp": None}
