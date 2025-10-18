from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from uuid import uuid4
import os
import re

def validate_phone(value):
    pattern = r'^\+7\d{10}$'
    if not re.match(pattern, value):
        raise ValidationError('Номер телефона должен быть в формате +7XXXXXXXXXX')
    
def validate_inn(value):

    inn_str = str(value)

    if len(inn_str) not in [12]:
        raise ValidationError(message='ИНН должен содержать 12 цифр')
    
    if not inn_str.isdigit():
        raise ValidationError(message='ИНН должен содержать только цифры')
    
def validate_passport(value):
    if len(value) != 11:
        raise ValidationError('Серия и номер паспорта должны содержать 10 символов')

def validate_postal_code(value):
    if len(value) != 6:
        raise ValidationError('Почтовый индекс должен содержать 6 цифр')
    if not value.isdigit():
        raise ValidationError('Почтовый индекс должен содержать только цифры')
    
def validate_price(value):
    if not re.match(r'^\d*\.?\d*$', value):
        raise ValidationError('Стоимость должна содержать только цифры и точку')
    # if int(value) <= 0:
    #     raise ValidationError('Стоимость должна быть положительным числом')
    
def profile_doc_upload_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    new_name = f"{uuid4().hex}.{ext}"
    return os.path.join("documents", str(instance.user.id), new_name)

def clean_document_photo(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Максимальный размер файла 5MB")
    

class Profile(models.Model):

    DOCUMENT_CHOICES = [
        ('Паспорт', 'Паспорт'),
    ]
    PURCHASE_CHOICES = [
        ('Первичный', 'Первичный'),
        ('Вторичный', 'Вторичный'),
    ]
    STATUS_CHOICES = [
        ('Обработка', 'Обработка'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    surname = models.CharField( max_length=30,
                                verbose_name='Отчество',
                                default='',
                                blank=True,
                                validators=[RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Отчество может содержать только русские буквы')]
                                )
    
    phone = models.CharField(max_length=12,
                             verbose_name='Номер телефона',
                             blank=True,
                             default='',
                             validators=[validate_phone]
                             )
    
    agree_to_terms = models.BooleanField(verbose_name='Согдасие на обработку данных',
                                         null=True,
                                         default=True
                                         )
    
    document_type = models.CharField(max_length=20, 
                                     verbose_name='Документ',
                                     choices=DOCUMENT_CHOICES, default='Паспорт',
                                     )

    id_document = models.CharField(max_length=11,
                                   verbose_name='Серия и номер паспорта',
                                   blank=True,
                                   default='',
                                   validators=[validate_passport])
    
    issued_by_whom = models.CharField( max_length=50,
                                verbose_name='Орган, выдавший документ',
                                default='',
                                blank=True,
                                )

    inn = models.CharField(max_length=12,
                           verbose_name='ИНН',
                           blank=True,
                           default='',
                           validators=[validate_inn]
                           )

    type_of_purchase = models.CharField(max_length=10, 
                                        verbose_name='Тип покупки',
                                        choices=PURCHASE_CHOICES,
                                        default='Первичный')
    
    status = models.CharField(max_length=25, 
                                        verbose_name='Статус',
                                        choices=STATUS_CHOICES,
                                        default='Обработка')

    price = models.CharField(max_length=12, 
                             verbose_name='Стоимость объекта недвижимости',
                             blank=True,
                             default='',
                             validators=[validate_price])

    price_in_queue = models.CharField(max_length=15, 
                                      verbose_name='Стоимость объекта при переходе в очередь',
                                      blank=True,
                                      default='',
                                      validators=[validate_price])

    birth_date = models.DateField(max_length=10, 
                                  verbose_name='Дата рождения',
                                  blank=True,
                                  null=True,
                                  default=None)

    date_of_issue = models.DateField(max_length=10,
                                     verbose_name='Дата выдачи',
                                     blank=True,
                                     null=True, 
                                     default=None)

    id_coor = models.CharField(max_length=24,
                               verbose_name='Номер счёта',
                               blank=True,
                               default='',
                               validators=[RegexValidator(r'^[0-9A-Za-z-]+$', 'Номер счёта может содержать только цифры и латинские буквы и дефис')])

    parther_name = models.CharField(max_length=60,
                                    verbose_name='Фамилия и имя партнёра',
                                    blank=True,
                                    default='',
                                    validators=[RegexValidator(r'^[а-яА-ЯёЁ\s]+$', 'ФИО партнёра может содержать только русские буквы и пробелы')])

    parther_phone = models.CharField(max_length=12,
                                     verbose_name='Номер телефона',
                                     blank=True,
                                     default='',
                                     validators=[validate_phone])
    
    document_photo_main = models.ImageField(
                                    upload_to=profile_doc_upload_path,
                                    verbose_name="Фото главной старницы",
                                    null=True,
                                    blank=True,
                                    default='',
                                    validators=[clean_document_photo]
                                    )
    
    document_photo_reg = models.ImageField(
                                    upload_to=profile_doc_upload_path,
                                    verbose_name="Фото прописки",
                                    null=True,
                                    blank=True,
                                    default='',
                                    validators=[clean_document_photo]
                                    )
    
    can_edit = models.BooleanField(
        default=True,
        verbose_name="Редактирование"
    )

    history = HistoricalRecords()

    def clean(self):
        super().clean()
        
        if self.birth_date and self.date_of_issue:
            if self.date_of_issue <= self.birth_date:
                raise ValidationError('Дата выдачи не может быть раньше даты рождения')
        
        # if self.price and self.price_in_queue:
        #     if int(self.price_in_queue) > int(self.price):
        #         raise ValidationError('Стоимость в очереди не может быть больше исходной стоимости')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.phone}"
    

class Profile_address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile_address')
    
    reg_country = models.CharField(max_length=50, verbose_name='Страна', default='')
    reg_region = models.CharField(max_length=50, verbose_name='Регион', default='')
    reg_city = models.CharField(max_length=30, verbose_name='Город', default='')
    reg_address = models.CharField(max_length=100, verbose_name='Адрес', default='')
    reg_street = models.CharField(max_length=50, verbose_name='Улица', default='')
    reg_house = models.CharField(max_length=20, verbose_name='Дом', default='')
    reg_apartament = models.CharField(max_length=20, verbose_name='Квартира', default='')

    reg_postal_code = models.CharField(max_length=6, 
                                       verbose_name='Почтовый индекс', 
                                       default='', 
                                       validators=[validate_postal_code])

    is_approved = models.BooleanField(max_length=5, verbose_name='Подтверждение', null=True, default=False)
    info = models.BooleanField(max_length=1, null=True, default=False)

    act_country = models.CharField(max_length=50, verbose_name='Страна', default='')
    act_region = models.CharField(max_length=50, verbose_name='Регион', default='')
    act_city = models.CharField(max_length=30, verbose_name='Город', default='')
    act_address = models.CharField(max_length=100, verbose_name='Адрес', default='')
    act_street = models.CharField(max_length=50, verbose_name='Улица', default='')
    act_house = models.CharField(max_length=20, verbose_name='Дом', default='')
    act_apartament = models.CharField(max_length=20, verbose_name='Квартира', default='')

    act_postal_code = models.CharField(max_length=6, 
                                       verbose_name='Почтовый индекс', 
                                       default='', 
                                       validators=[validate_postal_code])

    
    def __str__(self):
        return f" {self.user.email}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if hasattr(instance, 'profile'):
#         instance.profile.save()
