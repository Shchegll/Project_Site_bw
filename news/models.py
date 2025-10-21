from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class News(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Текст новости')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="news", verbose_name='Автор')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


    def __str__(self):
        return self.title
