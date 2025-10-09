from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "personal_account"

urlpatterns = [
    path("", views.AccountPageView.as_view(), name="account"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.CustomRegistrationView.as_view(), name="signup"),
    path('requisites/', views.CustomRequisitesView.as_view(), name="requisites"),
    path('plug/', views.CustomPlugView.as_view(), name="plug"),
    path('plug_1/', views.CustomPlugView.as_view(), name="plug_1"),
    path('plug_2/', views.CustomPlugView.as_view(), name="plug_2"),
    path('plug_3/', views.CustomPlugView.as_view(), name="plug_3"),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name="personal_account/password_reset.html",
        email_template_name="personal_account/password_reset_email.html",
        success_url='/personal_account/password_reset/done/'
    ), name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="personal_account/password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/',views.CustomPasswordResetConfirmView.as_view(),name="password_reset_confirm"),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="personal_account/password_reset_complete.html"), name="password_reset_complete"),
    path('<str:username>/profile_edit', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
]
