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
from .forms import LoginForm, RegistrationForm, ProfileUpdateForm, ProfileAddresForm, ProfileInviteeForm, ProfileQueueForm
from django.core.exceptions import ValidationError
from .models import Profile, Profile_addres, Profile_invitee, Profile_queue
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.views import View
from django.db import transaction
from django.utils import timezone
from . import utils as reg_utils


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


class CustomHelpView(TemplateView):
    template_name = "personal_account/help.html"


class CustomRequisitesView(TemplateView):
    template_name = "personal_account/requisites.html"


class RegistrationStartView(View):
    template_name = 'personal_account/signup.html'
    form_class = RegistrationForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'title': 'Регистрация на сайте'})

    def post(self, request):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            form.add_error('email', "Пользователь с таким email уже существует.")
            return render(request, self.template_name, {'form': form})

        if not reg_utils.can_send_code(email):
            messages.error(request, "Слишком много попыток отправки. Попробуйте позже.")
            return render(request, self.template_name, {'form': form})

        code = reg_utils.generate_code(6)

        hashed_password = make_password(form.cleaned_data['password1'])

        data = {
            'email': email,
            'username': email,
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'phone': form.cleaned_data['phone'],
            'agree_to_terms': form.cleaned_data['agree_to_terms'],
            'password_hash': hashed_password,
            'created_at': timezone.now().isoformat(),
        }

        reg_utils.cache_registration_data(code, email, data)
        reg_utils.send_confirmation_email(email, code)

        request.session['pending_email'] = email

        return render(request, 'personal_account/verify_email.html', {'email': email})


class VerifyRegistrationView(View):
    template_name = 'personal_account/verify_email.html'

    def get(self, request):
        email = request.session.get('pending_email', '')
        return render(request, self.template_name, {'email': email})

    def post(self, request):
        input_code = request.POST.get('code', '').strip()
        data = reg_utils.get_registration_data_by_code(input_code)
        if not data:
            messages.error(request, "Код неверный или просрочен. Попробуйте запросить код заново.")
            return render(request, self.template_name, {'email': request.session.get('pending_email', '')})

        email = data['email']
        if User.objects.filter(email=email).exists():
            messages.error(request, "Пользователь с таким email уже зарегистрирован.")
            reg_utils.delete_registration_data(input_code, email)
            return redirect(reverse_lazy('personal_account:login'))

        try:
            with transaction.atomic():
                user = User.objects.create(
                    username=data['username'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    password=data['password_hash'],
                )

                profile_defaults = {
                    'phone': data.get('phone', ''),
                    'agree_to_terms': data.get('agree_to_terms', False),
                    'can_edit': True,
                }

                Profile.objects.update_or_create(user=user, defaults=profile_defaults)

        except ValidationError as e:
            reg_utils.delete_registration_data(input_code, email)
            request.session.pop('pending_email', None)
            return redirect(reverse('personal_account:signup'))

        reg_utils.delete_registration_data(input_code, email)
        request.session.pop('pending_email', None)

        login(request, user)
        messages.success(request, "Email подтверждён. Заполните, пожалуйста, основные поля профиля.")
        return redirect(reverse('personal_account:user_profile', kwargs={'username': request.user.username}))


class ResendCodeView(View):
    def post(self, request):
        email = request.POST.get('email') or request.session.get('pending_email')
        if not email:
            messages.error(request, "Email не указан. Пожалуйста, заполните форму регистрации заново.")
            return redirect(reverse('personal_account:signup'))

        existing_code = reg_utils.get_code_by_email(email)
        if existing_code:
            if not reg_utils.can_send_code(email):
                messages.error(request, "Слишком много попыток отправки. Попробуйте позже.")
                return redirect(reverse('personal_account:signup'))
            reg_utils.send_confirmation_email(email, existing_code)
            messages.info(request, f"Код повторно отправлен на {email}.")
            request.session['pending_email'] = email
            return redirect(reverse('personal_account:verify_email'))

        messages.error(request, "Данные регистрации не найдены или просрочены. Пожалуйста, заполните форму заново.")
        return redirect(reverse('personal_account:signup'))


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


class ProfileUpdateChoiceView(LoginRequiredMixin, TemplateView):
    template_name = 'personal_account/profile_edit/profile_edit_choice.html'

    def dispatch(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.can_edit == "False":
            messages.error(request, "Редактирование заблокировано. При ошибке обратитесь к администратору.")
            return redirect("personal_account:user_profile", username=request.user.username)
        return super().dispatch(request, *args, **kwargs)


class PersonalInformationUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'personal_account/profile_edit/profile_edit_personal_information.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def dispatch(self, request, *args, **kwargs):
        profile = self.get_object()
        if not profile.can_edit:
            messages.error(request, "Редактирование заблокировано. При ошибке обратитесь к администратору.")
            return redirect("personal_account:user_profile", username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            address = self.request.user.profile_addres
        except Profile_addres.DoesNotExist:
            address = Profile_addres(user=self.request.user)
        if 'address_form' not in context:
            context['address_form'] = ProfileAddresForm(instance=address)
        context['dadata_token'] = settings.TOKEN
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        try:
            address_inst = request.user.profile_addres
        except Profile_addres.DoesNotExist:
            address_inst = Profile_addres(user=request.user)
        address_form = ProfileAddresForm(request.POST, instance=address_inst)

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

        user = profile.user
        user.first_name = form.cleaned_data.get('first_name', user.first_name)
        user.last_name  = form.cleaned_data.get('last_name', user.last_name)
        user.save()

        if profile.can_edit == "True":
            profile.can_edit = "One_done"

            profile.save()

            addr = address_form.save(commit=False)
            addr.user = self.request.user
            addr.save()

            messages.success(self.request, "Личные данные успешно обновлены. Заполните следующий блок")
            return redirect(self.get_success_url())

        if profile.can_edit == "Changes_one":
            profile.can_edit = "False"

            profile.save()

            addr = address_form.save(commit=False)
            addr.user = self.request.user
            addr.save()

            messages.success(self.request, "Личные данные успешно обновлены.")
            return redirect(self.get_success_url_else())

        else:
            profile.can_edit = "False"

            profile.save()

            addr = address_form.save(commit=False)
            addr.user = self.request.user
            addr.save()

            messages.success(self.request, "Личные данные успешно обновлены.")
            return redirect(self.get_success_url_else())

    def form_invalid(self, form, address_form=None):
        context = self.get_context_data(form=form, address_form=address_form)
        context['dadata_token'] = settings.TOKEN
        return self.render_to_response(context)

    def get_success_url_else(self):
        return reverse('personal_account:user_profile', kwargs={'username': self.request.user.username})

    def get_success_url(self):
        return reverse('personal_account:profile_edit_choice', kwargs={'username': self.request.user.username})


class PurchaseInformationUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile_queue
    form_class = ProfileQueueForm
    template_name = 'personal_account/profile_edit/profile_edit_purchase_information.html'

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile_queue
        except Profile_queue.DoesNotExist:
            return Profile_queue.objects.create(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.can_edit == "False":
            messages.error(request, "Редактирование заблокировано. При ошибке обратитесь к администратору.")
            return redirect(self.get_success_url_else())
        if profile.can_edit == "True":
            messages.error(request, "Сначала заполните предыдущий блок")
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url_else(self):
        return reverse('personal_account:user_profile', kwargs={'username': self.request.user.username})

    def get_success_url(self):
        return reverse('personal_account:profile_edit_choice', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        self.object = form.save()
        profile = self.request.user.profile

        if profile.can_edit == "Changes_two":
            profile.can_edit = "False"
            profile.save()
            messages.success(self.request, "Информация о покупке успешно обновлена")
            return redirect(self.get_success_url())

        else:
            profile.can_edit = "Two_done"
            profile.save()
            messages.success(self.request, "Информация о покупке успешно обновлена.")
            return redirect(self.get_success_url())


class SourceInformationnUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile_invitee
    form_class = ProfileInviteeForm
    template_name = 'personal_account/profile_edit/profile_edit_source_information.html'

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile_invitee
        except Profile_invitee.DoesNotExist:
            return Profile_invitee.objects.create(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.can_edit == "False":
            messages.error(request, "Редактирование заблокировано. При ошибке обратитесь к администратору.")
            return redirect(self.get_success_url_else())
        if profile.can_edit == "One_done":
            messages.error(request, "Сначала заполните предыдущий блок")
            return redirect(self.get_success_url())
        if profile.can_edit == "True":
            messages.error(request, "Сначала заполните предыдущий блок")
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url_else(self):
        return reverse('personal_account:user_profile', kwargs={'username': self.request.user.username})

    def get_success_url(self):
        return reverse('personal_account:profile_edit_choice', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        self.object = form.save()
        profile = self.request.user.profile

        if profile.can_edit == "Two_done":
            profile.can_edit = "False"
            profile.save()
            messages.success(self.request, "Вся информация успешно обновлена")
            return redirect(self.get_success_url())

        elif profile.can_edit == "Changes_three":
            profile.can_edit = "False"
            profile.save()
            messages.success(self.request, "Информация о пригласившем успешно обновлена.")
            return redirect(self.get_success_url_else())

        else:
            profile.can_edit = "False"
            profile.save()
            messages.success(self.request, "Информация о пригласившем успешно обновлена.")
            return redirect(self.get_success_url_else())
