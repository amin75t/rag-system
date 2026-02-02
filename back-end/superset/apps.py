from django.apps import AppConfig


class SupersetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'superset'
    verbose_name = 'Superset Integration'
    
    def ready(self):
        """Initialize app when Django starts"""
        pass
