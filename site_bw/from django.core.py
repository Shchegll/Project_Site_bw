from django.core.mail import send_mail

EMAIL_HOST = 'mail.hosting.reg.ru'  # или smtp.yourdomain.com
EMAIL_PORT = 587  # Рекомендуется для REG.ru
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'recovery@bestwaycoop.ru'
EMAIL_HOST_PASSWORD = '123456789!_'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# Простое текстовое письмо
send_mail(
    'Тестовое письмо из Django',
    'Привет! Это тестовое письмо. Если ты это видишь - почта работает!',
    EMAIL_HOST_USER,
    ['yariksglv@gmail.com'],  # Замените на ваш реальный email
    fail_silently=False,
)

print("Письмо отправлено!")