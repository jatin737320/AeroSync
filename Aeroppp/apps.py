from django.apps import AppConfig


class AeropppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Aeroppp"


class AeropppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Aeroppp'

    def ready(self):
        import Aeroppp.signals  # Import signals module