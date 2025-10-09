from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Profile, Profile_address

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'surname', 'phone', 'document_type', 'status', 'id_document', 'issued_by_whom', 'inn', 'get_document_photo_main', 'get_document_photo_reg']
    list_filter = ['document_type', 'type_of_purchase', 'can_edit']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'surname', 'phone', 'inn']
    readonly_fields = ['get_document_photo_main_preview', 'get_document_photo_reg_preview']
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'surname', 'phone', 'birth_date')
        }),
        ('Документы', {
            'fields': ('document_type', 'id_document', 'date_of_issue', 'issued_by_whom', 'inn', 
                      'document_photo_main', 'get_document_photo_main_preview',
                      'document_photo_reg', 'get_document_photo_reg_preview')
        }),
        ('Информация о покупке', {
            'fields': ('type_of_purchase', 'price', 'price_in_queue', 'status')
        }),
        ('Партнерская информация', {
            'fields': ('parther_name', 'parther_phone', 'id_coor')
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

@admin.register(Profile_address)
class ProfileAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'reg_country', 'reg_city', 'reg_address', 'is_approved', 'info']
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
            'fields': ( 'info', )
        }),
    )