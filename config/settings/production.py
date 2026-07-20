import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403, F401

DEBUG = False

SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

sentry_sdk.init(
    dsn=env("SENTRY_DSN", default=None),  # noqa: F405
    integrations=[DjangoIntegration()],
    send_default_pii=False,
    traces_sample_rate=0.2,
    environment="production",
)
