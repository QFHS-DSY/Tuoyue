from .settings import *  # noqa

DEBUG = True

# Fast and dependency-light test DB.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable read replica and routers for isolated test run.
DATABASE_ROUTERS = []

# Keep tests deterministic and fast.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CELERY_TASK_ALWAYS_EAGER = True
DEMO_MODE = False
SMS_DEBUG_BYPASS_CODE = ""
SMS_EXPOSE_CODE_IN_RESPONSE = True
SMS_SEND_MIN_INTERVAL_SECONDS = 0
SMS_SEND_IP_MIN_INTERVAL_SECONDS = 0
SMS_SEND_DAILY_LIMIT_PHONE = 0
SMS_CAPTCHA_REQUIRED = False
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
ASGI_APPLICATION = "myproject.asgi.application"
