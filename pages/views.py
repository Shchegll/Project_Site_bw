# pages/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from news.models import News

class AboutPageView(TemplateView):
    template_name = "pages/home_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем важные новости (последние 3)
        context['important_news'] = News.objects.filter(
            is_important=True
        ).order_by('-created_at')[:3]
        return context

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
