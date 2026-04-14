from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-room/', views.create_room, name='create_room'),
    path('room/', views.room, name='room'),
    path('room/<slug:room_id>/', views.room, name='room_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]
