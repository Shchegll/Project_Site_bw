# pages/views.py
from django.shortcuts import render
from django.views.generic import TemplateView

class AboutPageView(TemplateView):
    template_name = "pages/home_page.html"

class CustomDonationView(TemplateView):
    template_name = "pages/donation.html"

def handler403(request, exception):
    template = "pages/403csrf.html"
    return render(request, template, status=403)


def handler404(request, exception):
    template = "pages/404.html"
    return render(request, template, status=404)


def handler500(request):
    template = "pages/500.html"
    return render(request, template, status=500)
