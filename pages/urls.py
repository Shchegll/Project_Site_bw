# pages/urls
from django.urls import path
from . import views

urlpatterns = [
    path("", views.AboutPageView.as_view(), name="home"),
    path("pages/", views.AboutPageView.as_view(), name="about"),
    path('donation/', views.CustomDonationView.as_view(), name="donation"),
]
