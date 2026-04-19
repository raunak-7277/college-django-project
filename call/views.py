import uuid
from django.shortcuts import render, redirect


def home(request):
    return render(request, 'home.html')


def create_room(request):
    room_id = str(uuid.uuid4())[:8]  
    return redirect('room_detail', room_id=room_id)

def room(request, room_id):
    return render(request, 'room.html', {'room_id': room_id})


def login_view(request):
    return render(request, 'login.html')


def register_view(request):
    return render(request, 'register.html')
