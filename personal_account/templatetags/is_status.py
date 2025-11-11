from django import template
from .utils import user_is_status

register = template.Library()

@register.filter
def is_status_template(user):
    return user_is_status(user)
