from django.urls import path
from . import views


urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('signup/', views.RegisterUserView.as_view(), name='signup'),
]
