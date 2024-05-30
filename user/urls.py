from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('signup/', views.RegisterUserView.as_view(), name='signup'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
