from django.apps import AppConfig


class ShortviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shortview'
    
    def ready(self):
        from .jobs import start_job_scheduler
        start_job_scheduler()
