def user_is_staff(user):
    if not user or user.is_anonymous:
        return False
    if getattr(user, "info", False):
        return True
    # если у вас профиль: user.profile.is_staff
    profile = getattr(user, "profile_addres", None)
    if profile and getattr(profile, "info", False):
        return True
    return False


# def user_is_staff(user):
#     if not user or user.is_anonymous:
#         return False
#     if getattr(user, "can_edit", False):
#         return True
#     # если у вас профиль: user.profile.is_staff
#     profile = getattr(user, "profile", None)
#     if profile and getattr(profile, "can_edit", False):
#         return True
#     return False