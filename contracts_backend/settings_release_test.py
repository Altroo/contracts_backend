"""Isolated release tests and previews; never use the configured app database."""
import getpass
import os

from .settings_test import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/contracts-release-preview.sqlite3",
        "TEST": {"NAME": ":memory:"},
    }
}
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
# Keep historical models registered so migration state matches production.
INSTALLED_APPS = [*INSTALLED_APPS, "simple_history"]  # noqa: F405
CORS_ALLOWED_ORIGINS = ["http://localhost:8947"]
CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS

# Full-text search requires PostgreSQL. Use a disposable local cluster only.
if os.environ.get("CONTRACTS_RELEASE_POSTGRES_PORT"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "127.0.0.1",
            "PORT": os.environ["CONTRACTS_RELEASE_POSTGRES_PORT"],
            "NAME": "postgres",
            "USER": getpass.getuser(),
            "TEST": {
                "NAME": "contracts_release_isolated_test",
                "CHARSET": "UTF8",
                "TEMPLATE": "template0",
            },
        }
    }
