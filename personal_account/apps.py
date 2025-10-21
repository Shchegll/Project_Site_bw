from django.apps import AppConfig


class PersonalAccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personal_account'
    verbose_name = 'База персональных данных'
    verbose_name_plural = "База персональных данных"

