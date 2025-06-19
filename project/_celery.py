#C:\Users\MD BASARULL ISLAM\Downloads\adcpaapi1-main (1)\adcpaapi1-main\project\_celery.py
import os
from celery import Celery

# Django settings সেট করা
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# আগের মতো নাম রাখতে চাইলে _celery নাম ব্যবহার করো
_celery = Celery('adcpa-platform')

# Redis broker URL
_celery.conf.broker_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Django settings থেকে কনফিগ লোড করা
_celery.config_from_object('django.conf:settings', namespace='CELERY')

# সব অ্যাপে টাস্ক খুঁজে বের করা
_celery.autodiscover_tasks()

# Optional: Extra config
_celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
)

# Optional: Periodic tasks (beat)
_celery.conf.beat_schedule = {
    'cache-offers': {
        'task': 'offer.tasks.cache_offers.cache_offers',
        'schedule': 60,
    },
}
