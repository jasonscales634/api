from .admin_dashboard import CustomAdminSite
from ._celery import _celery as celery_app

__all__ = ['celery_app']
