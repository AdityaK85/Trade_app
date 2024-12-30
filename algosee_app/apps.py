from django.apps import AppConfig


class AlgoseeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'algosee_app'
    def ready(self):
        import algosee_app.signal