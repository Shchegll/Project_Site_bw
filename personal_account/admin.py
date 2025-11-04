from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Profile, Profile_address, Profile_invitee, Profile_partner, Profile_queue

admin.site.site_header = "Панель администратора"
admin.site.index_title = "Управление сайтом"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'surname',
                    'phone',
                    'document_type',
                    'id_document',
                    'issued_by_whom',
                    'issued_by_whom',
                    'inn',
                    'get_document_photo_main',
                    'get_document_photo_reg'
                    ]

    list_filter = ['document_type',
                   'can_edit'
                   ]

    search_fields = ['user_email',
                     'user_first_name',
                     'user_last_name',
                     'surname',
                     'phone',
                     'inn'
                     ]

    readonly_fields = ['get_document_photo_main_preview',
                       'get_document_photo_reg_preview'
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
                    'reg_country',
                    'reg_city',
                    'reg_address',
                    'is_approved',
                    'info']
    list_filter = ['reg_country', 'is_approved']
    search_fields = ['user__email', 'reg_city', 'reg_address']
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


@admin.register(Profile_invitee)
class ProfileinviteeAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'parther_name',
                    'parther_phone',
                    ]

    search_fields = [
        'parther_name',
        'parther_phone'
    ]

    fieldsets = (
        ('Информация о пригошении', {
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
        'status',
        'type_of_purchase',
        'price',
        'price_in_queue',
        'id_coor',
        'contract_photo_preview',
    ]

    list_filter = [
        'status',
        'type_of_purchase',
    ]

    search_fields = [
        'id_coor',
        'price',
        'price_in_queue'
    ]

    readonly_fields = ['contract_photo_preview', 'share_payment_photo_preview', 'membership_fee_photo_preview']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user',
                'status',
                'type_of_purchase',
                'price',
                'price_in_queue',
                'id_coor'
            )
        }),
        ('Документы', {
            'fields': (
                'contract_photo',
                'contract_photo_preview',
                'share_payment_photo',
                'share_payment_photo_preview',
                'membership_fee_photo',
                'membership_fee_photo_preview',
            )
        }),
    )

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
        'referral_code',
        'referred',
        'referral_link',
    ]

    readonly_fields = [
        'referral_code',
        'referral_link',
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'referral_code',
                'referral_link',
            )
        }),
        ('Реферальная система', {
            'fields': (
                'referred',
            )
        }),
    )

    def referral_link_display(self, obj):
        if obj.referral_link:
            return mark_safe(f'<a href="{obj.referral_link}" target="_blank">{obj.referral_link}</a>')
        return "Нет ссылки"
    referral_link_display.short_description = 'Реферальная ссылка'

    def referred_by(self, obj):
        if obj.referred:
            return obj.referred.email
        return "Не приглашен"
    referred_by.short_description = 'Приглашен пользователем'
