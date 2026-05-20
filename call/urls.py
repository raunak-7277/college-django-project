from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('create-room/', views.create_room, name='create_room'),
    path('join-room/', views.join_room, name='join_room'),
    path('room/<slug:room_id>/', views.room, name='room_detail'),
    path('meeting/<slug:room_id>/end/', views.end_meeting, name='end_meeting'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('meetings/', views.meeting_history, name='meeting_history'),
    path('subscription/', views.subscription_page, name='subscription'),
    path('buy-plan/<int:plan_id>/', views.buy_plan, name='buy_plan'),
    path('approve-payment/<int:proof_id>/',views.approve_payment,name='approve_payment'),
]
