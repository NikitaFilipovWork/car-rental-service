from django.apps import AppConfig


class CarConfig(AppConfig):
    name = "car"

    def ready(self):
        import car.signals  # noqa: F401
