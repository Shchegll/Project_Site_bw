from django.contrib import admin
from django.utils.safestring import mark_safe
from . import models as md
from django.utils.html import format_html
from django.utils import timezone

admin.site.site_header = "Панель администратора"
admin.site.index_title = "Управление сайтом"


@admin.register(md.Profile)
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


@admin.register(md.Profile_address)
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


@admin.register(md.Profile_invitee)
class ProfileinviteeAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'parther_name',
                    'parther_phone',
                    ]

    list_filter = ['parther_phone']

    readonly_fields = [
        'user',
    ]

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


@admin.register(md.Profile_queue)
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


@admin.register(md.Profile_partner)
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


@admin.register(md.SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'status_display',
        'created_at',
    ]

    list_filter = [
        'status',
        'priority',
        'notification_type',
        'created_at',
    ]

    search_fields = [
        'title',
        'message',
        'status',
        'notification_type',
        'created_at'
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'notification_type'
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'message')
        }),
        ('Настройки уведомления', {
            'fields': ('status', 'priority', 'notification_type')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        status_colors = {
            'Обработка': 'orange',
            'Кандидат': 'blue',
            'Член потребительского кооператива': 'green',
            'Пайщик': 'darkgreen',
            'Консультант': 'purple',
            'Исключён': 'red',
            'Архив': 'gray',
            '': 'lightgray'
        }
        color = status_colors.get(obj.status, 'lightgray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Статус'

    def priority_display(self, obj):
        priority_colors = {
            1: 'green',   # Низкий
            2: 'orange',  # Средний
            3: 'red'      # Высокий
        }
        color = priority_colors.get(obj.priority, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_display.short_description = 'Приоритет'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(md.MessageNotification)
class MessageNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'to_user',
        'is_read_display',
        'read_at',
        'created_at'
    ]

    list_filter = [
        'is_read',
        'created_at',
        'read_at',
        'to_user'
    ]

    search_fields = [
        'title',
        'message',
        'to_user__username',
        'to_user__email',
        'to_user__first_name',
        'to_user__last_name'
    ]

    readonly_fields = [
        'created_at',
        'read_at'
    ]

    autocomplete_fields = ['to_user']

    fieldsets = (
        ('Получатель', {
            'fields': ('to_user',)
        }),
        ('Содержание сообщения', {
            'fields': ('title', 'message')
        }),
        ('Статус прочтения', {
            'fields': ('is_read', 'read_at'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def is_read_display(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Прочитано</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Не прочитано</span>'
            )
    is_read_display.short_description = 'Статус прочтения'

    def mark_as_read(self, request, queryset):
        updated = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        self.message_user(
            request, 
            f'{updated} сообщений помечено как прочитанные'
        )
    mark_as_read.short_description = 'Пометить выбранные как прочитанные'

    actions = ['mark_as_read']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('to_user')

    def save_model(self, request, obj, form, change):
        # Автоматически устанавливаем read_at при отметке как прочитанное
        if obj.is_read and not obj.read_at:
            obj.read_at = timezone.now()
        elif not obj.is_read:
            obj.read_at = None
        super().save_model(request, obj, form, change)
