from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('boards/', views.create_board_view, name='create_board'),
    path('boards/<int:board_id>/', views.handle_board_view, name='board'),
]
