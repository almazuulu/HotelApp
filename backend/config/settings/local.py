"""Local development settings: the Docker Compose runtime on a developer machine.

This environment is never exposed publicly. There is no production settings module,
and none is planned for the MVP.
"""

from .base import *  # noqa: F403
from .base import env_bool

DEBUG = env_bool("DJANGO_DEBUG", True)

# Password reset uses standard Django tokens; mail is printed to the container log.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
