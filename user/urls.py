from django.contrib.auth.views import (LogoutView, PasswordChangeDoneView,
                                       PasswordChangeView)
from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.RegisterUserView.as_view(), name='signup'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
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
]
