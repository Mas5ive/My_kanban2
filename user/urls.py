from django.contrib.auth.views import (LogoutView, PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path, reverse_lazy

from . import OAuth2, views

urlpatterns = [
    path('signup/', views.RegisterUserView.as_view(), name='signup'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout/redirect-to-OAuth2/select-<str:provider>/', OAuth2.logout_then_OAuth2, name='logout_then_OAuth2'),
    path(
        'password-change/',
        PasswordChangeView.as_view(template_name='user/password_change.html'),
        name='password_change'
    ),
    path(
        'password-change/done/',
        PasswordChangeDoneView.as_view(template_name='user/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password-reset/',
        PasswordResetView.as_view(
            template_name='user/password_reset.html',
            email_template_name='user/password_reset_email.html',
            success_url=reverse_lazy('password_reset_done')
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='user/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset/complete/',
        PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
