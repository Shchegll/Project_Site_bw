def user_is_status(user):
    if not user or user.is_anonymous:
        return False
    profile = getattr(user, "profile_queue", None)
    if profile and getattr(profile, "status", False) == "Консультант":
        return "Консультант"
    if profile and getattr(profile, "status", False) == "Обработка":
        return "Обработка"
    if profile and getattr(profile, "status", False) == "Пайщик":
        return "Пайщик"
    if profile and getattr(profile, "status", False) == "Участник":
        return "Участник"
    if profile and getattr(profile, "status", False) == "Кандидат":
        return "Кандидат"
    return False
