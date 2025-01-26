# apps.py
from django.apps import AppConfig
import threading

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplikacja'

    def ready(self):
        # Uruchom wątek po pełnym załadowaniu aplikacji
        from .wateringControl import measure_parameters

        thread = threading.Thread(target=measure_parameters, daemon=True)
        thread.start()
