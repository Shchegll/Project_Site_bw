from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Profile, Profile_address, Profile_invitee, Profile_partner, Profile_queue

admin.site.site_header = "Панель администратора"
admin.site.index_title = "Управление сайтом"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'get_first_name',
                    'get_last_name',
                    'surname',
                    'phone',
                    ]

    search_fields = ['user__email',
                     'user__first_name',
                     'user__last_name',
                     'surname',
                     'phone',
                     'inn'
                     ]

    readonly_fields = ['get_document_photo_main_preview',
                       'get_document_photo_reg_preview',
                       'agree_to_terms'
                       ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'surname', 'phone', 'birth_date')
        }),
        ('Документы', {
            'fields': ('document_type',
                       'id_document',
                       'date_of_issue',
                       'issued_by_whom',
                       'inn',
                       'document_photo_main',
                       'get_document_photo_main_preview',
                       'document_photo_reg',
                       'get_document_photo_reg_preview'
                       )
        }),
        ('Настройки', {
            'fields': ('can_edit', 'agree_to_terms')
        }),
    )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'Имя'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Фамилия'

    def get_document_photo_main(self, obj):
        if obj.document_photo_main:
            return "Есть фото"
        return "Нет фото"
    get_document_photo_main.short_description = 'Основное фото документа'

    def get_document_photo_reg(self, obj):
        if obj.document_photo_reg:
            return "Есть фото"
        return "Нет фото"
    get_document_photo_reg.short_description = 'Фото регистрации'

    def get_document_photo_main_preview(self, obj):
        if obj.document_photo_main:
            return mark_safe(f'<img src="{obj.document_photo_main.url}" width="350" />')
        return "Нет изображения"
    get_document_photo_main_preview.short_description = 'Предпросмотр основного фото'

    def get_document_photo_reg_preview(self, obj):
        if obj.document_photo_reg:
            return mark_safe(f'<img src="{obj.document_photo_reg.url}" width="350" />')
        return "Нет изображения"
    get_document_photo_reg_preview.short_description = 'Предпросмотр фото регистрации'

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'can_edit':
            kwargs['choices'] = [
                ('True', 'Разрешить полное редактирование'),
                ('False', 'Запретить редактирование'),
                ('Changes_one', 'Разрешить редактирование 1 блока'),
                ('Changes_two', 'Разрешить редактирование 2 блока'),
                ('Changes_three', 'Разрешить редактирование 3 блока'),
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(Profile_address)
class ProfileAddressAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'get_first_name',
                    'get_last_name',
                    'info'
                    ]

    list_filter = ['reg_country', 'reg_region', 'reg_city', 'info']
    search_fields = ['user__email',
                     'user__first_name',
                     'user__last_name',
                     'user__email',
                     'reg_city',
                     'reg_address'
                     ]

    fieldsets = (
        ('Адрес регистрации', {
            'fields': (
                'reg_country', 'reg_region', 'reg_city',
                'reg_address', 'reg_street', 'reg_house',
                'reg_apartament', 'reg_postal_code'
            )
        }),
        ('Адрес проживания', {
            'fields': (
                'act_country', 'act_region', 'act_city',
                'act_address', 'act_street', 'act_house',
                'act_apartament', 'act_postal_code', 'is_approved'
            )
        }),
        ('Инфа', {
            'fields': ('info',)
        }),
        )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'Имя'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Фамилия'

    def get_info(self, obj):
        return obj.info
    get_info.short_description = 'Информация'


@admin.register(Profile_invitee)
class ProfileinviteeAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'parther_name',
                    'parther_phone',
                    ]

    list_filter = ['parther_phone']

    search_fields = [
        'user__email',
        'parther_name',
        'parther_phone'
    ]

    fieldsets = (
        ('Информация о приглошении', {
            'fields': (
                'user',
                'parther_name',
                'parther_phone',
            )
        }),
    )


@admin.register(Profile_queue)
class ProfileQueueAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'get_first_name',
        'get_last_name',
        'status',
        'id_coor',
    ]

    list_filter = [
        'status',
        'additional_status',
        'agree_to_consultant',
    ]

    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'id_coor',
    ]

    readonly_fields = ['contract_photo_preview', 'share_payment_photo_preview', 'membership_fee_photo_preview', 'consultant_contract_photo_preview', 'user']

    fieldsets = (
        ('Информация о покупке', {
            'fields': (
                'user',
                'type_of_purchase',
                'price',
                'price_in_queue',
                'id_coor',
            )
        }),
        ('Основные документы', {
            'fields': (
                'contract_photo',
                'contract_photo_preview',
                'share_payment_photo',
                'share_payment_photo_preview',
                'membership_fee_photo',
                'membership_fee_photo_preview',
            ),
            'classes': ('collapse',)
        }),
        ('Статус и подтверждающие документы', {
            'fields': (
                'status',
                'agree_to_consultant',
                'additional_status',
                'consultant_contract_photo',
                'consultant_contract_photo_preview',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'Имя'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Фамилия'

    def consultant_contract_photo_preview(self, obj):
        if obj.consultant_contract_photo:
            return mark_safe(f'<img src="{obj.consultant_contract_photo.url}" style="max-height: 100px;" />')
        return "Нет изображения"
    consultant_contract_photo_preview.short_description = 'Предпросмотр'

    def contract_photo_preview(self, obj):
        if obj.contract_photo:
            return mark_safe(f'<img src="{obj.contract_photo.url}" style="max-height: 100px;" />')
        return "Нет изображения"
    contract_photo_preview.short_description = 'Предпросмотр'

    def share_payment_photo_preview(self, obj):
        if obj.share_payment_photo:
            return mark_safe(f'<img src="{obj.share_payment_photo.url}" style="max-height: 100px;" />')
        return "Нет изображения"
    share_payment_photo_preview.short_description = 'Предпросмотр'

    def membership_fee_photo_preview(self, obj):
        if obj.membership_fee_photo:
            return mark_safe(f'<img src="{obj.membership_fee_photo.url}" style="max-height: 100px;" />')
        return "Нет изображения"
    membership_fee_photo_preview.short_description = 'Предпросмотр'


@admin.register(Profile_partner)
class ProfilePartnerAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'get_first_name',
        'get_last_name',
        'referral_code',
        'referred',
    ]

    readonly_fields = ['referral_code', 'consultant_level']

    autocomplete_fields = ['referred']

    # Добавьте поисковые поля для autocomplete
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    list_filter = ['referred']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'referral_code',
                'consultant_level',
            )
        }),
        ('Реферальная система', {
            'fields': (
                'referred',
            )
        }),
    )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'Имя'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Фамилия'
