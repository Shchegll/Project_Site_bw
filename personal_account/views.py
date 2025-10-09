# personal_account/views.py
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordResetConfirmView
from django.views.generic import TemplateView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import LoginForm, RegistrationForm, ProfileUpdateForm, ProfileAddressForm
from .models import Profile, Profile_address
from django.conf import settings


class AccountPageView(TemplateView):
    template_name = "personal_account/personal_account.html"


class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'personal_account/login.html'
    extra_context = {'title': 'Авторизация на сайте'}

    def get_success_url(self):
        return reverse_lazy('home')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "personal_account/password_reset_confirm.html"
    success_url = reverse_lazy('personal_account:password_reset_complete')

class CustomPlugView(TemplateView):
    template_name = "personal_account/plug.html"

class CustomRequisitesView(TemplateView):
    template_name = "personal_account/requisites.html"

class CustomRegistrationView(CreateView):  
    form_class = RegistrationForm  
    template_name = 'personal_account/signup.html'  
    extra_context = {'title': 'Регистрация на сайте'}  

    def get_success_url(self):  
        return reverse_lazy('personal_account:login')  

    def form_valid(self, form):  
        return super().form_valid(form)


class UserProfileView(TemplateView):  
    template_name = 'personal_account/profile_page.html'  

    def get_context_data(self, **kwargs):  
        context = super().get_context_data(**kwargs)  
        try:  
            user = get_object_or_404(User, username=self.kwargs.get('username'))  
        except User.DoesNotExist:  
            raise Http404("Пользователь не найден")  
        context['user_profile'] = user  
        context['title'] = f'Профиль пользователя {user}'  
        return context  

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'personal_account/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def dispatch(self, request, *args, **kwargs):
        profile = self.get_object()
        if not profile.can_edit:
            messages.error(request, "Редактирование заблокировано. Обратитесь к администратору.")
            return redirect("personal_account:user_profile", username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # если адреса нет — создаём пустой экземпляр, но не сохраняем
        try:
            address = self.request.user.profile_address
        except Profile_address.DoesNotExist:
            address = Profile_address(user=self.request.user)
        # если уже есть в kwargs (например при POST с ошибками) — используем его
        if 'address_form' not in context:
            context['address_form'] = ProfileAddressForm(instance=address)
        context['dadata_token'] = settings.TOKEN
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        # при POST формируем адресную форму с данными
        try:
            address_inst = request.user.profile_address
        except Profile_address.DoesNotExist:
            address_inst = Profile_address(user=request.user)
        address_form = ProfileAddressForm(request.POST, instance=address_inst)

        if form.is_valid() and address_form.is_valid():
            return self.forms_valid(form, address_form)
        else:
            return self.form_invalid(form, address_form)

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        return initial

    def forms_valid(self, form, address_form):
        profile = form.save(commit=False)

        # сохраняем имена в связанном User
        user = profile.user
        user.first_name = form.cleaned_data.get('first_name', user.first_name)
        user.last_name  = form.cleaned_data.get('last_name', user.last_name)
        user.save()

        # сохраняем профиль и блокируем повторное редактирование
        profile.can_edit = False
        profile.save()

        # сохраняем адрес (update_or_create не обязателен, т.к. у нас instance)
        addr = address_form.save(commit=False)
        addr.user = self.request.user
        addr.save()

        messages.success(self.request, "Данные успешно обновлены. Повторное редактирование запрещено.")
        return redirect(self.get_success_url())

    def form_invalid(self, form, address_form):
        # показать шаблон с обеими формами и ошибками
        context = self.get_context_data(form=form, address_form=address_form)
        context['dadata_token'] = settings.TOKEN
        return render(self.request, self.template_name, context, {
            'form': form,
            'address_form': address_form
        })

    def get_success_url(self):
        return reverse('personal_account:user_profile', kwargs={'username': self.request.user.username})
