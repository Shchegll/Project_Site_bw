from django.contrib import admin
from .models import News

admin.site.site_header = "Панель администратора"
admin.site.index_title = "Управление сайтом"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # Поля, которые отображаются в списке
    list_display = ['title', 'author', 'created_at', 'updated_at']
    
    # Поля для фильтрации справа
    list_filter = ['created_at', 'updated_at', 'author']
    
    # Поля для поиска
    search_fields = ['title', 'content']
    
    # Поля, которые можно редактировать прямо из списка
    # list_editable = []
    
    # Автоматическое заполнение slug (если нужно)
    # prepopulated_fields = {"slug": ("title",)}
    
    # Разбивка формы на секции
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content')
        }),
        ('Дополнительная информация', {
            'fields': ('author', 'created_at', 'updated_at'),
            'classes': ('collapse',)  # Сворачиваемая секция
        }),
    )
    
    # Только для чтения поля
    readonly_fields = ['updated_at']
    
    # Автоматическое определение автора
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)