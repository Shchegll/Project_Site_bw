from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from . import models as md

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email',
            'required': True
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

    class Meta:
        model = User
        fields = ['username', 'password']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email',
            'required': True
        })
    )
    first_name = forms.CharField(
        max_length=30,
        label='Имя',
        validators=[md.RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Имя может содержать только русские буквы')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя',
            'required': True,
        })
    )
    last_name = forms.CharField(
        max_length=30,
        label='Фамилия',
        validators=[md.RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Фамилия может содержать только русские буквы')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию',
            'required': True
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
        })
    )
    password1 = forms.CharField(
        max_length=128,
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'required': True
        })
    )
    password2 = forms.CharField(
        max_length=128,
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
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
        fields = ['email', 'first_name', 'last_name', 'phone', 'password1', 'password2', 'agree_to_terms']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # логинимся по email
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, created = md.Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data['phone']
            profile.agree_to_terms = self.cleaned_data['agree_to_terms']
            profile.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        label="Имя",
        validators=[md.RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Имя может содержать только русские буквы')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        label="Фамилия",
        validators=[md.RegexValidator(r'^[а-яА-ЯёЁ]+$', 'Фамилия может содержать только русские буквы')],
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
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    inn = forms.CharField(
        required=True,
        max_length=12,
        label="ИНН",
        validators=[md.validate_inn],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    type_of_purchase = forms.ChoiceField(
        required=True,
        label="Тип покупки",
        choices=md.Profile.PURCHASE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        required=False,
        label="Статус",
        choices=md.Profile.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.CharField(
        required=True,
        max_length=12,
        label="Стоимость объекта недвижимости",
        validators=[md.validate_price],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    price_in_queue = forms.CharField(
        max_length=15,
        label="Стоимость объекта недвижимости при переходе в очередь",
        validators=[md.validate_price],
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
    id_coor = forms.CharField(
        required=False,
        max_length=24,
        label="Номер счёта",
        validators=[md.RegexValidator(r'^[0-9A-Za-z-]+$', 'Номер счёта может содержать только цифры и латинские буквы и дефис')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите 17 чисел',
            })
    )
    parther_name = forms.CharField(
        required=True,
        max_length=60,
        label="ФИО",
        validators=[md.RegexValidator(r'^[а-яА-ЯёЁ\s]+$', 'ФИО может содержать только русские буквы и пробелы')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
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
                  'parther_name', 
                  'parther_phone',
                  'id_coor', 
                  'birth_date', 
                  'document_type', 
                  'id_document', 
                  'date_of_issue',
                  'issued_by_whom', 
                  'inn', 
                  'type_of_purchase', 
                  'status',
                  'price', 
                  'price_in_queue',
                  'document_photo_main',
                  'document_photo_reg'
                  ]

        widgets = {
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control',
                                                    'placeholder': '+7...'
                                                    }
                                            ),
            'parther_phone': forms.TextInput(attrs={'class': 'form-control',
                                                    'placeholder': '+7...'
                                                    }
                                            ),
            'type_of_purchase': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'document_photo_main': forms.FileInput(), # <- убираем поле очистки фото
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

        if self.instance and self.instance.type_of_purchase:
            self.fields['type_of_purchase'].required = True

        if self.instance and self.instance.status:
            self.fields['status'].required = False

        if self.instance and self.instance.price:
            self.fields['price'].required = True

        if self.instance and self.instance.price_in_queue:
            self.fields['price_in_queue'].required = True

        if self.instance and self.instance.parther_name:
            self.fields['parther_name'].required = True

        if self.instance and self.instance.birth_date:
            self.fields['birth_date'].required = True

        if self.instance and self.instance.date_of_issue:
            self.fields['date_of_issue'].required = True  

        if self.instance and self.instance.id_coor:
            self.fields['id_coor'].required = True

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

            if self.instance.type_of_purchase and not cleaned_data.get('type_of_purchase'):
                self.add_error('type_of_purchase', 'Это поле обязательно')

            if self.instance.price and not cleaned_data.get('price'):
                self.add_error('price', 'Это поле обязательно')

            if self.instance.price_in_queue and not cleaned_data.get('price_in_queue'):
                self.add_error('price_in_queue', 'Это поле обязательно')
                
            if self.instance.birth_date and not cleaned_data.get('birth_date'):
                self.add_error('birth_date', 'Это поле обязательно')

            if self.instance.parther_name and not cleaned_data.get('parther_name'):
                self.add_error('parther_name', 'Это поле обязательно')

            if self.instance.date_of_issue and not cleaned_data.get('date_of_issue'):
                self.add_error('date_of_issue', 'Это поле обязательно')
            
            if self.instance.id_coor and not cleaned_data.get('id_coor'):
                self.add_error('id_coor', 'Это поле обязательно')

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
    required=False,
    max_length = 50,
    label="Страна регистрации",
    widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reg_region = forms.CharField(
        required=True,
        max_length = 150,
        label="Регион регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reg_city = forms.CharField(
        required=True,
        max_length = 150,
        label="Город регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reg_address = forms.CharField(
        required=True,
        max_length = 250,
        label="Полный адрес регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reg_street = forms.CharField(
        required=False,
        max_length = 150,
        label="Улица регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reg_house = forms.CharField(
        required=True,
        max_length = 20,
        label="Дом регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reg_apartament = forms.CharField(
        required=True,
        max_length = 20,
        label="Квартира регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reg_postal_code = forms.CharField(
        required=True,
        max_length=6,
        label="Почтовый индекс регистрации",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_country = forms.CharField(
        max_length = 50,
        label="Страна проживания",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_region = forms.CharField(
        max_length = 150,
        label="Регион проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_city = forms.CharField(
        max_length = 150,
        label="Город проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_address = forms.CharField(
        max_length = 250,
        label="Полный адрес проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_street = forms.CharField(
        max_length = 150,
        required=False,
        label="Улица проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_house = forms.CharField(
        max_length = 20,
        label="Дом проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_apartament = forms.CharField(
        max_length = 20,
        label="Квартира проживания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    act_postal_code = forms.CharField(
        max_length=6,
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
                  'is_approved']

        widgets = {
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
            addr = super().save(commit=False)
            if commit:
                addr.save()
            return addr
