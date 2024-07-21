
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomPasswordChangeForm, LoginUserForm, RegisterUserForm


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
