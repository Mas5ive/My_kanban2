
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import (LoginView, PasswordChangeView,
                                       PasswordResetConfirmView,
                                       PasswordResetView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import (CustomPasswordChangeForm, CustomPasswordResetForm,
                    CustomSetPasswordForm, LoginUserForm, RegisterUserForm)


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password1')
        )
        login(self.request, user)
        return response


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = 'auth/login.html'


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'user/password_change.html'


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'user/password_reset.html'
    email_template_name = 'user/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
