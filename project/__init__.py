# Makes Celery functionality optional.
try:
    from project.celery import app as celery_app

    __all__ = ("celery_app",)
except ImportError:
    pass
