"""Deterministic settings for the backend test suite."""

from .base import *  # noqa: F403

SECRET_KEY = "test-only-secret-key"
DEBUG = False

# Unit and API-contract tests do not need a running Docker PostgreSQL container.
# PostgreSQL-specific behaviour is exercised separately when the occupancy ledger
# exists; this scaffold has no database-specific domain behaviour yet.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
