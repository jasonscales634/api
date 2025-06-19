import os
import dj_database_url
from .base import *

# =============================
# 🔐 Secret Key
# =============================
SECRET_KEY = os.environ.get('DJ_SECRET_KEY', 'fallback-secret')

# =============================
# 🗄️ Database
# =============================
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        engine='django.db.backends.postgresql_psycopg2',
    )
}

# =============================
# ✅ Logging
# =============================
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure logs directory exists

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django_warning.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# =============================
# 🛡️ Sentry integration (Optional)
# =============================
if os.getenv("SENTRY_DSN"):
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=os.environ["SENTRY_DSN"],
            integrations=[DjangoIntegration()],
            traces_sample_rate=0.5,
            send_default_pii=True
        )
    except ImportError:
        print("⚠️ sentry-sdk not installed. Skipping Sentry setup.")
