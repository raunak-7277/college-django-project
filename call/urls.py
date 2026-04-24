from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-room/', views.create_room, name='create_room'),
    path('join-room/', views.join_room, name='join_room'),
    path('room/<slug:room_id>/', views.room, name='room_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('meetings/', views.meeting_history, name='meeting_history'),
]