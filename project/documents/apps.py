from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project.documents'
    verbose_name = _('Documents')

    def ready(self):
        from project.documents import signals
        super().ready()
