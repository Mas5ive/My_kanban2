from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/invitations/boards/<int:board_id>/', views.pick_invitation_view, name='pick_invitation'),
    path('boards/', views.create_board_view, name='create_board'),
    path('boards/<int:board_id>/', views.handle_board_view, name='board'),
    path('boards/<int:board_id>/invitations/', views.сreate_invitation_view, name='сreate_invitation'),
    path('boards/<int:board_id>/members/', views.delete_member_view, name='delete_member'),
]
