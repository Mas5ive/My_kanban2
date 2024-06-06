from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       UsernameField)
from django.utils.translation import gettext_lazy as _


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Username')
    email = forms.EmailField(label='Email', widget=forms.EmailInput())
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']


class LoginUserForm(AuthenticationForm):
    extend_label = 'Username or email'

    username = UsernameField(
        label=extend_label,
        error_messages={
            'required': _(extend_label + " is required."),
        },
        widget=forms.TextInput(attrs={
            "autofocus": True,
            'id': 'id_username_or_email',
        }),
    )

    error_messages = {
        "invalid_login": _(
            f"Please enter a correct {extend_label.lower()} and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
