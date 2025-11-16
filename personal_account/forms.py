from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, FileExtensionValidator
from . import models as md


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email',
            'required': True,
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        max_length=128,
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'required': True
        })
    )

    agree_to_terms = forms.BooleanField(
        label='Согласен с условиями обработки персональных данных',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': True
        })
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'agree_to_terms']


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email',
            'required': True,
            'autocomplete': 'email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        label='Имя',
        validators=[RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Поле -Имя- может содержать только русские буквы')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя',
            'required': True,
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        label='Фамилия',
        validators=[RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Поле -Фамилия- может содержать только русские буквы')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию',
            'required': True,
            'autocomplete': 'family-name'
        })
    )
    phone = forms.CharField(
        max_length=12,
        label='Номер телефона',
        validators=[md.validate_phone],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7XXXXXXXXXX',
            'required': True,
            'autocomplete': 'tel'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        label="Имя",
        validators=[RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Поле -Имя- может содержать только русские буквы')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        label="Фамилия",
        validators=[RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Поле -Фамилия- может содержать только русские буквы')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    document_type = forms.ChoiceField(
        required=True,
        label="Тип документа",
        choices=md.Profile.DOCUMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    id_document = forms.CharField(
        required=True,
        max_length=11,
        label="Серия и номер паспорта",
        validators=[md.validate_passport],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    issued_by_whom = forms.CharField(
        required=True,
        max_length=50,
        label="Орган, выдавший документ",
        validators=[RegexValidator(r'^[а-яА-ЯёЁ\s]+$', 'Поле -Орган, выдавший документ- может содержать только русские буквы и пробелы')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    inn = forms.CharField(
        required=True,
        max_length=12,
        label="ИНН",
        validators=[md.validate_inn],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        label="Дата рождения",
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            },
            format='%Y-%m-%d'
        )
    )
    date_of_issue = forms.DateField(
        label="Дата выдачи",
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            },
            format='%Y-%m-%d'
        )
    )
    document_photo_main = forms.FileField(
        required=True,
        label="Фото главной страницы",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    document_photo_reg = forms.FileField(
        required=True,
        label="Фото прописки",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = md.Profile
        fields = ['last_name',
                  'first_name',
                  'surname',
                  'phone',
                  'birth_date',
                  'document_type',
                  'id_document',
                  'date_of_issue',
                  'issued_by_whom',
                  'inn',
                  'document_photo_main',
                  'document_photo_reg'
                  ]

        widgets = {
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': '+7...'
                                            }),
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'document_photo_main': forms.FileInput(),
            'document_photo_reg': forms.FileInput()
        }

    def clean_document_photo(self):
        photo_fields = ['document_photo_main', 'document_photo_reg']
        for f in photo_fields:
            f = self.cleaned_data.get('document_photo')
            if f and f.size > 5 * 1024 * 1024:
                raise md.ValidationError("Файл слишком большой (макс 5MB).")
            return f

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.birth_date:
            self.fields['birth_date'].initial = self.instance.birth_date

        if self.instance.date_of_issue:
            self.fields['date_of_issue'].initial = self.instance.date_of_issue

        if self.instance and self.instance.document_type:
            self.fields['document_type'].required = True

        if self.instance and self.instance.id_document:
            self.fields['id_document'].required = True

        if self.instance and self.instance.issued_by_whom:
            self.fields['issued_by_whom'].required = True

        if self.instance and self.instance.inn:
            self.fields['inn'].required = True

        if self.instance and self.instance.birth_date:
            self.fields['birth_date'].required = True

        if self.instance and self.instance.date_of_issue:
            self.fields['date_of_issue'].required = True

        if self.instance and self.instance.document_photo_main:
            self.fields['document_photo_main'].required = True

        if self.instance and self.instance.document_photo_reg:
            self.fields['document_photo_reg'].required = True

    def clean(self):
        cleaned_data = super().clean()

        if self.instance:
            if self.instance.document_type and not cleaned_data.get('document_type'):
                self.add_error('document_type', 'Это поле обязательно')

            if self.instance.id_document and not cleaned_data.get('id_document'):
                self.add_error('id_document', 'Это поле обязательно')

            if self.instance.issued_by_whom and not cleaned_data.get('issued_by_whom'):
                self.add_error('issued_by_whom', 'Это поле обязательно')

            if self.instance.inn and not cleaned_data.get('inn'):
                self.add_error('inn', 'Это поле обязательно')

            if self.instance.birth_date and not cleaned_data.get('birth_date'):
                self.add_error('birth_date', 'Это поле обязательно')

            if self.instance.date_of_issue and not cleaned_data.get('date_of_issue'):
                self.add_error('date_of_issue', 'Это поле обязательно')

            if self.instance.document_photo_main and not cleaned_data.get('document_photo_main'):
                self.add_error('document_photo_main', 'Это поле обязательно')

            if self.instance.document_photo_reg and not cleaned_data.get('document_photo_reg'):
                self.add_error('document_photo_reg', 'Это поле обязательно')

        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        user.first_name = self.cleaned_data.get('first_name', user.first_name)

        if commit:
            user.save()
            profile.save()
        return profile


class ProfileAddressForm(forms.ModelForm):
    reg_country = forms.CharField(
        required=True,
        max_length=50,
        label="Страна регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
        )
    reg_region = forms.CharField(
        required=True,
        max_length=150,
        label="Регион регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    reg_city = forms.CharField(
        required=True,
        max_length=150,
        label="Город регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    reg_address = forms.CharField(
        required=True,
        max_length=250,
        label="Полный адрес регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    reg_street = forms.CharField(
        required=False,
        max_length=150,
        label="Улица регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    reg_house = forms.CharField(
        required=True,
        max_length=20,
        label="Дом регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    reg_apartament = forms.CharField(
        required=True,
        max_length=20,
        label="Квартира регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    reg_postal_code = forms.CharField(
        required=True,
        max_length=6,
        label="Почтовый индекс регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_country = forms.CharField(
        max_length=50,
        label="Страна проживания",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    act_region = forms.CharField(
        max_length=150,
        required=False,
        label="Регион проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    act_city = forms.CharField(
        max_length=150,
        required=False,
        label="Город проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    act_address = forms.CharField(
        max_length=250,
        required=False,
        label="Полный адрес проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    act_street = forms.CharField(
        max_length=150,
        required=False,
        label="Улица проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    act_house = forms.CharField(
        max_length=20,
        required=False,
        label="Дом проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    act_apartament = forms.CharField(
        max_length=20,
        required=False,
        label="Квартира проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[md.validate_no_english]
    )
    act_postal_code = forms.CharField(
        max_length=6,
        required=False,
        label="Почтовый индекс проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_approved = forms.BooleanField(
        label='Адрес регистрации совпадает с адресом проживания',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            })
            )

    class Meta:
        model = md.Profile_address
        fields = ['reg_country',
                  'reg_region',
                  'reg_city',
                  'reg_address',
                  'reg_street',
                  'reg_house',
                  'reg_apartament',
                  'reg_postal_code',
                  'act_country',
                  'act_region',
                  'act_city',
                  'act_address',
                  'act_street',
                  'act_house',
                  'act_apartament',
                  'act_postal_code',
                  'is_approved'
                  ]

        widgets = {
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        addr = super().save(commit=False)
        if commit:
            addr.save()
        return addr


class ProfileInviteeForm(forms.ModelForm):
    parther_name = forms.CharField(max_length=60,
                                   label='Фамилия и имя партнёра',
                                   required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   validators=[RegexValidator(r'^[а-яА-ЯёЁ\s]+$', 'Поле -ФИО партнёра- может содержать только русские буквы и пробелы')]
                                   )

    parther_phone = forms.CharField(max_length=12,
                                    label='Номер телефона',
                                    required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                                    validators=[md.validate_phone]
                                    )

    class Meta:
        model = md.Profile_invitee
        fields = ['parther_name',
                  'parther_phone',
                  ]

    def save(self, commit=True):
        profile_invitee = super().save(commit=False)

        if commit:
            profile_invitee.save()

        return profile_invitee


class ProfileQueueForm(forms.ModelForm):
    type_of_purchase = forms.ChoiceField(
        label='Тип покупки',
        required=False,
        choices=md.Profile_queue.PURCHASE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    status = forms.ChoiceField(
        label='Статус',
        required=False,
        choices=md.Profile_queue.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    price = forms.CharField(
        max_length=12,
        label='Стоимость объекта недвижимости',
        required=False,
        validators=[md.validate_price],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    price_in_queue = forms.CharField(
        max_length=15,
        label='Стоимость объекта при переходе в очередь',
        required=False,
        validators=[md.validate_price],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    id_coor = forms.CharField(
        max_length=24,
        label='Номер счёта',
        required=False,
        validators=[RegexValidator(r'^[0-9A-Za-z-]+$', 'Номер счёта может содержать только цифры и латинские буквы и дефис')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    contract_photo = forms.FileField(
        required=False,
        label="Договор/Соглашение",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    share_payment_photo = forms.FileField(
        required=False,
        label="Последняя квитанция об оплате паевого взноса",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    membership_fee_photo = forms.FileField(
        required=False,
        label="Последня квитанция об оплате членского взноса",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = md.Profile_queue
        fields = [
            'type_of_purchase',
            'status',
            'price',
            'price_in_queue',
            'id_coor',
            'contract_photo',
            'share_payment_photo',
            'membership_fee_photo'
        ]

    def clean_document_photo(self):
        photo_fields = ['contract_photo', 'share_payment_photo', 'membership_fee_photo']
        for f in photo_fields:
            f = self.cleaned_data.get('document_photo')
            if f and f.size > 5 * 1024 * 1024:
                raise md.ValidationError("Файл слишком большой (макс 5MB).")
            return f


class ProcessingApplicationForm(forms.ModelForm):
    class Meta:
        model = md.Profile_queue
        fields = ['consultant_contract_photo', 'agree_to_consultant']
        widgets = {
            'consultant_contract_photo': forms.FileInput(attrs={'required': 'required'}),
            'agree_to_consultant': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'required': 'required'
                }),
        }
        labels = {
            'consultant_contract_photo': 'Загрузите фото',
            'agree_to_consultant': 'Я согласен с условиями',
        }


class FeedbackForm(forms.Form):
    subject = forms.CharField(
        max_length=50,
        label='Тема обращения',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Краткое описание'
        })
    )
    message = forms.CharField(
        label='Подробное описание проблемы',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Опишите проблему максимально подробно...'
        })
    )
    photo = forms.ImageField(
        required=False,
        label='Прикрепить скриншот (если нужно)',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        })
    )

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("Файл слишком большой. Максимальный размер 5MB.")
        return photo
