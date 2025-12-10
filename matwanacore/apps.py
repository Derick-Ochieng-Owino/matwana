from django.apps import AppConfig


class MatwanacoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matwanacore'

    def ready(self):
        import matwanacore.signals