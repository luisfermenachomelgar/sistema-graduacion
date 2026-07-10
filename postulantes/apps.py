from django.apps import AppConfig


class PostulantesConfig(AppConfig):
    name = 'postulantes'

    def ready(self):
        import postulantes.signals  # noqa: F401
