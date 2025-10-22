from django import template
from .utils import user_is_staff

register = template.Library()

@register.filter
def is_staff_template(user):
    return user_is_staff(user)
