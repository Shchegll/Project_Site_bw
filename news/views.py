# news/views.py
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .models import News
from .forms import NewsForm
from .utils import user_is_staff


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return user_is_staff(self.request.user)

    def handle_no_permission(self):
        raise PermissionDenied


class NewsListView(ListView):
    model = News
    template_name = "news/news_page.html"
    paginate_by = 10

    def get_queryset(self):
        return News.objects.all().order_by('-is_important', '-created_at')


class NewsDetailView(DetailView):
    model = News
    template_name = "news/news_detail.html"
    context_object_name = "detail"


class NewsCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = "news/news_page.html"
    success_url = reverse_lazy("news:news_page")

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'id': self.object.pk})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)


class NewsUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = News
    form_class = NewsForm
    template_name = "news/news_page.html"
    success_url = reverse_lazy("news:news_page")

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)


class NewsDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = News
    template_name = "news/news_confirm_delete.html"
    success_url = reverse_lazy("news:news_page")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        pk = self.object.pk

        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        )

        if is_ajax:
            self.object.delete()
            return JsonResponse({'success': True, 'id': pk})
        return super().delete(request, *args, **kwargs)
