def user_is_staff(user):
    if not user or user.is_anonymous:
        return False
    profile = getattr(user, "profile_address", None)
    if profile and getattr(profile, "info", False):
        return True
    return False
