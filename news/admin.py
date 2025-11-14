from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from .models import News

admin.site.site_header = "Панель администратора"
admin.site.index_title = "Управление сайтом"


class NewsAdminForm(forms.ModelForm):
    class Meta:
        model = News
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = User.objects.filter(is_staff=True)


class StaffUserFilter(admin.SimpleListFilter):
    title = 'автор'
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        # Все staff-пользователи
        staff_users = User.objects.filter(is_staff=True)
        return [(user.id, user.username) for user in staff_users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(author__id=self.value())
        return queryset


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):

    form = NewsAdminForm

    list_display = ['title', 'author', 'is_important', 'created_at']

    list_filter = ['created_at', 'updated_at', StaffUserFilter]

    search_fields = ['title', 'content']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content')
        }),
        ('Дополнительная информация', {
            'fields': ('author', 'is_important', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['updated_at']

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
