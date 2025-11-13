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
    if profile and getattr(profile, "status", False) == "Член потребительского кооператива":
        return "Член потребительского кооператива"
    if profile and getattr(profile, "status", False) == "Кандидат":
        return "Кандидат"
    if profile and getattr(profile, "status", False) == "Архив":
        return "Архив"
    if profile and getattr(profile, "status", False) == "Исключён":
        return "Исключён"
    return False


def agree_to_consultant(user):

    profile = getattr(user, "profile_queue", None)
    if profile and getattr(profile, "agree_to_consultant", False) is True:
        return True
    return False
