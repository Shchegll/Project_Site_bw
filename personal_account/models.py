from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from uuid import uuid4
import random
import string
import os
import re


def validate_phone(value):
    pattern = r'^\+7\d{10}$'
    if not re.match(pattern, value):
        raise ValidationError('Поле -Номер телефона- должно быть в формате +7XXXXXXXXXX')


# def validate_russian(text):
#     if not re.match(r'^[а-яА-ЯёЁ\s]+$', text):
#         raise ValidationError('Поле должно содержать только русские буквы и пробелы')


def validate_no_english(value):
    if re.search(r'[a-zA-Z]', value):
        raise ValidationError(f'Поле не должно содержать английские буквы')


def validate_inn(value):

    inn_str = str(value)

    if len(inn_str) not in [12]:
        raise ValidationError(message='Поле -ИНН- должно содержать 12 цифр')

    if not inn_str.isdigit():
        raise ValidationError(message='Поле -ИНН- должно содержать только цифры')


def validate_passport(value):
    if len(value) != 11:
        raise ValidationError('Поле -Серия и номер паспорта- должно содержать 10 символов')
    if not re.match(r'^[\d\s]+$', value):
        raise ValidationError('Поле -Серия и номер паспорта- должно содержать только цифры и пробелы')


def validate_postal_code(value):
    if len(value) != 6:
        raise ValidationError('Поле -Почтовый индекс- должно содержать 6 цифр')
    if not value.isdigit():
        raise ValidationError('Поле -Почтовый индекс- должно содержать только цифры')


def validate_price(value):
    if not re.match(r'^\d*\.?\d*$', value):
        raise ValidationError('Поле -Стоимость- должно содержать только цифры')
    # if int(value) <= 0:
    #     raise ValidationError('Стоимость должна быть положительным числом')


def get_profile_upload_path(instance, filename, file_type="document"):
    ext = filename.split('.')[-1].lower()

    folder_name = f"{instance.user.id}_{instance.user.first_name}_{instance.user.last_name}"

    templates = {
        "document_photo_main": f"Фото_главной_старницы{uuid4().hex}",
        "document_photo_reg": f"Фото_прописки{uuid4().hex}",
        "contract_photo": f"Договор_Соглашение{uuid4().hex}",
        "share_payment_photo": f"Последняя_квитанция_об_оплате_паевого_взноса{uuid4().hex}",
        "membership_fee_photo": f"Последня_квитанция_об_оплате_членского_взноса_{uuid4().hex}",
        "default": f"document_{uuid4().hex}"
    }

    new_filename = f"{templates.get(file_type, templates['default'])}.{ext}"

    return os.path.join("documents", folder_name, new_filename)


def document_photo_main_upload_path(instance, filename):
    return get_profile_upload_path(instance, filename, "document_photo_main")


def document_photo_reg_upload_path(instance, filename):
    return get_profile_upload_path(instance, filename, "document_photo_reg")


def contract_photo_upload_path(instance, filename):
    return get_profile_upload_path(instance, filename, "contract_photo")


def share_payment_photo_upload_path(instance, filename):
    return get_profile_upload_path(instance, filename, "share_payment_photo")


def membership_fee_photo_upload_path(instance, filename):
    return get_profile_upload_path(instance, filename, "membership_fee_photo")


def clean_document_photo(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Максимальный размер фото 5MB")


def validate_consultant_level(value):
    if value is not None and (value < 1 or value > 10):
        raise ValidationError('Уровень консультанта должен быть от 1 до 10')


class Profile(models.Model):

    DOCUMENT_CHOICES = [
        ('', '--- Выберите документ ---'),
        ('Паспорт', 'Паспорт'),
    ]
    CAN_EDIT_CHOICES = [
        ('True', 'Разрешить полное редактирование'),
        ('False', 'Запретить редактирование'),
        ('One_done', 'One_done'),
        ('Two_done', 'Two_done'),
        ('Changes_one', 'Разрешить редактирование 1 блока'),
        ('Changes_two', 'Разрешить редактирование 2 блока'),
        ('Changes_three', 'Разрешить редактирование 3 блока'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30,
                               verbose_name='Отчество',
                               default='',
                               blank=True,
                               validators=[RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Поле -Отчество- может содержать только русские буквы')]
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
                                     blank=True,
                                     choices=DOCUMENT_CHOICES,
                                     default='',
                                     )

    id_document = models.CharField(max_length=11,
                                   verbose_name='Серия и номер паспорта',
                                   blank=True,
                                   default='',
                                   validators=[validate_passport])

    issued_by_whom = models.CharField(max_length=50,
                                      verbose_name='Орган, выдавший документ',
                                      default='',
                                      blank=True,
                                      validators=[RegexValidator(r'^[а-яА-ЯёЁ\s\(\)]+$', 'Поле "Орган, выдавший документ" может содержать только русские буквы, пробелы и круглые скобки')]
                                      )

    inn = models.CharField(max_length=12,
                           verbose_name='ИНН',
                           blank=True,
                           default='',
                           validators=[validate_inn]
                           )

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

    document_photo_main = models.ImageField(
                                    upload_to=document_photo_main_upload_path,
                                    verbose_name="Фото главной старницы",
                                    null=True,
                                    blank=True,
                                    default='',
                                    validators=[clean_document_photo]
                                    )

    document_photo_reg = models.ImageField(
                                    upload_to=document_photo_reg_upload_path,
                                    verbose_name="Фото прописки",
                                    null=True,
                                    blank=True,
                                    default='',
                                    validators=[clean_document_photo]
                                    )

    can_edit = models.CharField(max_length=13,
                                default="True",
                                verbose_name='Разрешение на редактирование',
                                choices=CAN_EDIT_CHOICES,
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

    class Meta:
        verbose_name = "Личные данные"
        verbose_name_plural = "Личные данные"


class Profile_address(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='profile_address'
                                )

    reg_country = models.CharField(max_length=50,
                                   verbose_name='Страна',
                                   default='',
                                   validators=[validate_no_english]
                                   )

    reg_region = models.CharField(max_length=50,
                                  verbose_name='Регион',
                                  default='',
                                  validators=[validate_no_english]
                                  )

    reg_city = models.CharField(max_length=30,
                                verbose_name='Город',
                                default='',
                                validators=[validate_no_english]
                                )

    reg_address = models.CharField(max_length=100,
                                   verbose_name='Адрес',
                                   default='',
                                   validators=[validate_no_english]
                                   )

    reg_street = models.CharField(max_length=50,
                                  verbose_name='Улица',
                                  blank=True,
                                  null=True,
                                  default='',
                                  validators=[validate_no_english]
                                  )

    reg_house = models.CharField(max_length=20,
                                 verbose_name='Дом',
                                 default='',
                                 validators=[validate_no_english]
                                 )

    reg_apartament = models.CharField(max_length=20,
                                      verbose_name='Квартира',
                                      default='',
                                      validators=[validate_no_english]
                                      )

    reg_postal_code = models.CharField(max_length=6,
                                       verbose_name='Почтовый индекс',
                                       default='',
                                       validators=[validate_postal_code]
                                       )

    is_approved = models.BooleanField(max_length=5,
                                      verbose_name='Подтверждение',
                                      null=True,
                                      default=False
                                      )

    info = models.BooleanField(max_length=1, null=True, default=False)

    act_country = models.CharField(max_length=50,
                                   verbose_name='Страна',
                                   default='',
                                   validators=[validate_no_english]
                                   )

    act_region = models.CharField(max_length=50,
                                  verbose_name='Регион',
                                  default='',
                                  validators=[validate_no_english]
                                  )

    act_city = models.CharField(max_length=30,
                                verbose_name='Город',
                                default='',
                                validators=[validate_no_english]
                                )

    act_address = models.CharField(max_length=100,
                                   verbose_name='Адрес',
                                   default='',
                                   validators=[validate_no_english]
                                   )

    act_street = models.CharField(max_length=50,
                                  verbose_name='Улица',
                                  blank=True,
                                  null=True,
                                  default='',
                                  validators=[validate_no_english]
                                  )

    act_house = models.CharField(max_length=20,
                                 verbose_name='Дом',
                                 default='',
                                 validators=[validate_no_english]
                                 )

    act_apartament = models.CharField(max_length=20,
                                      verbose_name='Квартира',
                                      default='',
                                      validators=[validate_no_english]
                                      )

    act_postal_code = models.CharField(max_length=6,
                                       verbose_name='Почтовый индекс',
                                       default='',
                                       validators=[validate_postal_code]
                                       )

    history = HistoricalRecords()

    def __str__(self):
        return f" {self.user.email}"

    class Meta:
        verbose_name = "Регистрационные данные"
        verbose_name_plural = "Регистрационные данные"


class Profile_partner(models.Model):

    CONSULTANT_LEVEL_CHOICES = [
        (1, 'Уровень 1'),
        (2, 'Уровень 2'),
        (3, 'Уровень 3'),
        (4, 'Уровень 4'),
        (5, 'Уровень 5'),
        (6, 'Уровень 6'),
        (7, 'Уровень 7'),
        (8, 'Уровень 8'),
        (9, 'Уровень 9'),
        (10, 'Уровень 10'),
    ]

    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='profile_partner'
                                )

    referral_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Реферальный код'
    )
    referred = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        verbose_name='Приглашен пользователем'
    )
    referral_link = models.CharField(
        max_length=24,
        blank=True,
        null=True,
        verbose_name='Реферальная ссылка'
    )
    consultant_level = models.IntegerField(verbose_name='Уровень консультанта',
                                           choices=CONSULTANT_LEVEL_CHOICES,
                                           blank=True,
                                           null=True,
                                           default=None,
                                           validators=[validate_consultant_level]
                                           )

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        if not self.referral_link:
            self.referral_link = f"/register?ref={self.referral_code}"
        super().save(*args, **kwargs)

    def generate_referral_code(self):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        while Profile_partner.objects.filter(referral_code=code):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        return code

    history = HistoricalRecords()

    def __str__(self):
        return f" {self.user.email}"

    class Meta:
        verbose_name = "Информация о структура"
        verbose_name_plural = "Информация о структура"


class Profile_invitee(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='profile_invitee'
                                )

    parther_name = models.CharField(max_length=60,
                                    verbose_name='Фамилия и имя партнёра',
                                    blank=True,
                                    default='',
                                    validators=[RegexValidator(r'^[а-яА-ЯёЁ\s]+$', 'Поле -ФИО партнёра- может содержать только русские буквы и пробелы')]
                                    )

    parther_phone = models.CharField(max_length=12,
                                     verbose_name='Номер телефона',
                                     blank=True,
                                     default='',
                                     validators=[validate_phone]
                                     )

    history = HistoricalRecords()

    def __str__(self):
        return f" {self.user.email}"

    class Meta:
        verbose_name = "Информация о пригласившем"
        verbose_name_plural = "Информация о пригласившем"


class Profile_queue(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='profile_queue'
                                )

    PURCHASE_CHOICES = [
        ('', '--- Выберите тип ---'),
        ('Первичный', 'Первичный'),
        ('Вторичный', 'Вторичный'),
    ]
    STATUS_CHOICES = [
        ('Обработка', 'Обработка'),
        ('Кандидат', 'Кандидат'),
        ('Член потребительского кооператива', 'Член потребительского кооператива'),
        ('Пайщик', 'Пайщик'),
        ('Консультант', 'Консультант'),
        ('Исключён', 'Исключён'),
        ('Архив', 'Архив'),
    ]

    ADDITIONAL_STATUS_CHOICES = [
        ('', '--- Ничего не выбрано ---'),
        ('В очереди', 'В очереди'),
        ('На оформлении', 'На оформлении'),
        ('Формирование 35%', 'Формирование 35%'),
        ('Формирование 100%', 'Формирование 100%'),
        ('Должник', 'Должник'),
        ('Отсутствуют документы', 'Отсутствуют документы'),
        ('Процесс исключения', 'Процесс исключения'),
        ('Заявление пайщика', 'Заявление пайщика'),
        ('Решение совета', 'Решение совета'),
        ('Завершение целевой программы', 'Завершение целевой программы'),
    ]

    type_of_purchase = models.CharField(max_length=10,
                                        verbose_name='Тип покупки',
                                        choices=PURCHASE_CHOICES,
                                        default='',
                                        blank=True,
                                        )

    status = models.CharField(max_length=36,
                              verbose_name='Основоной статус пользователя',
                              choices=STATUS_CHOICES,
                              default='Обработка'
                              )

    consultant_contract_photo = models.ImageField(
                                    upload_to=contract_photo_upload_path,
                                    verbose_name="Заявление консультанта",
                                    null=True,
                                    blank=True,
                                    default='',
                                    validators=[clean_document_photo]
                                    )

    agree_to_consultant = models.BooleanField(verbose_name='Согдасие на присвоение статуса консультанта',
                                              null=True,
                                              default=False
                                              )

    additional_status = models.CharField(max_length=30,
                                         verbose_name='Дополнительный статус',
                                         choices=ADDITIONAL_STATUS_CHOICES,
                                         default=''
                                         )

    price = models.CharField(max_length=12,
                             verbose_name='Стоимость объекта недвижимости',
                             blank=True,
                             default='',
                             validators=[validate_price]
                             )

    price_in_queue = models.CharField(max_length=15,
                                      verbose_name='Стоимость объекта при переходе в очередь',
                                      blank=True,
                                      default='',
                                      validators=[validate_price]
                                      )

    id_coor = models.CharField(max_length=24,
                               verbose_name='Номер счёта',
                               blank=True,
                               default='',
                               validators=[RegexValidator(r'^[0-9A-Za-z-]+$', 'Номер счёта может содержать только цифры, латинские буквы и дефис')]
                               )

    contract_photo = models.ImageField(
                                    upload_to=contract_photo_upload_path,
                                    verbose_name="Договор/Соглашение",
                                    null=True,
                                    blank=True,
                                    default='',
                                    validators=[clean_document_photo]
                                    )

    share_payment_photo = models.ImageField(
                                    upload_to=share_payment_photo_upload_path,
                                    verbose_name="Последняя квитанция об оплате паевого взноса",
                                    null=True,
                                    blank=True,
                                    default='',
                                    validators=[clean_document_photo]
                                    )

    membership_fee_photo = models.ImageField(
                                    upload_to=membership_fee_photo_upload_path,
                                    verbose_name="Последня квитанция об оплате членского взноса",
                                    null=True,
                                    blank=True,
                                    default='',
                                    validators=[clean_document_photo]
                                    )

    history = HistoricalRecords()

    def __str__(self):
        return f" {self.user.email}"

    class Meta:
        verbose_name = "Информация о статусе"
        verbose_name_plural = "Информация о статусе"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
