from django import template
from .utils import user_is_status, agree_to_consultant

register = template.Library()

@register.filter
def is_status_template(user):
    return user_is_status(user)

@register.filter
def is_agree(user):
    return agree_to_consultant(user)
