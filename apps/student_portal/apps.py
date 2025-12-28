from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class StudentPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.student_portal'
    verbose_name = _('Student Portal')
