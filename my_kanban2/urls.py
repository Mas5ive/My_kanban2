"""
URL configuration for my_kanban2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import include, path
from thisapp import http_handlers

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('thisapp.urls')),
    path('', include('user.urls')),
    path('', include('social_django.urls', namespace='social')),
    path("__debug__/", include("debug_toolbar.urls")),
]

handler403 = http_handlers.permission_denied_view
handler404 = http_handlers.page_not_found_view
