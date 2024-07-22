from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       PasswordResetForm, SetPasswordForm,
                                       UserCreationForm, UsernameField)
from django.utils.translation import gettext_lazy as _


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password'}),
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']


class LoginUserForm(AuthenticationForm):
    extend_label = 'Username or email'
    password_label = 'Password'

    username = UsernameField(
        label=extend_label,
        error_messages={
            'required': _(extend_label + " is required."),
        },
        widget=forms.TextInput(attrs={
            "autofocus": True,
            'id': 'id_username_or_email',
            'placeholder': extend_label,
        }),
    )

    password = forms.CharField(
        label=_(password_label),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            'placeholder': password_label
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


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-field',
            'placeholder': 'Current Password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-field',
            'placeholder': 'New Password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-field',
            'placeholder': 'Confirm New Password'
        })
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-field',
            "autocomplete": "email",
            'placeholder': 'Enter your email',
        }),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(attrs={
            'class': 'form-field',
            "autocomplete": "new-password",
            'placeholder': 'New password'
        }),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-field',
            "autocomplete": "new-password",
            'placeholder': 'New password confirmation'
        }),
    )
