from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('profile/', views.profile_view, name='profile'),
    path('boards/<int:board_id>/', views.board_view, name='board'),
    path('boards/<int:board_id>/cards/', views.create_card_view, name='card_create'),
    path('boards/<int:board_id>/cards/<int:card_id>/', views.card_view, name='card'),
    path('boards/<int:board_id>/cards/<int:card_id>/comments/', views.create_comment_view, name='create_comment'),
    path(
        'boards/<int:board_id>/cards/<int:card_id>/comments/<int:comment_id>/',
        views.delete_comment_view,
        name='delete_comment',
    ),
    path(
        'boards/<int:board_id>/cards/<int:card_id>/comments/<int:comment_id>/file',
        views.get_file_from_comment,
        name='get_file_from_comment',
    ),
]
