from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import HttpResponseForbidden


@require_GET
@login_required
def protected_media(request, path):
    """
    Полностью запрещаем доступ к медиафайлам через прямые URL
    """
    return HttpResponseForbidden("Доступ к файлам запрещен")
