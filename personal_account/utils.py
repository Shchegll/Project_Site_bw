# personal_account/utils.py
import secrets
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.conf import settings

CODE_TIMEOUT_SECONDS = 15 * 60  # 15 минут

def generate_code(length=6):
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))

def _code_key(code):
    return f"reg:code:{code}"

def _email_key(email):
    return f"reg:email:{email}"

def cache_registration_data(code, email, data):
    # сохраняем по коду и по email (удобно для повторной отправки)
    cache.set(_code_key(code), data, CODE_TIMEOUT_SECONDS)
    cache.set(_email_key(email), code, CODE_TIMEOUT_SECONDS)
    return True

def get_registration_data_by_code(code):
    return cache.get(_code_key(code))

def get_code_by_email(email):
    return cache.get(_email_key(email))

def delete_registration_data(code, email=None):
    cache.delete(_code_key(code))
    if email:
        cache.delete(_email_key(email))

def send_confirmation_email(to_email, code):
    subject = "Код подтверждения регистрации"
    message = f"Ваш код для подтверждения регистрации: {code}\nОн действителен 15 минут."
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [to_email], fail_silently=False)

# Простая защита от частых отправок по email
def can_send_code(email, limit=5, period_seconds=3600):
    key = f"reg_rate:{email}"
    count = cache.get(key) or 0
    if count >= limit:
        return False
    if cache.get(key) is None:
        cache.set(key, 1, period_seconds)
    else:
        cache.incr(key)
    return True