from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def create_room(request):
    return render(request, 'create_room.html')


def room(request, room_id='demo-room'):
    context = {'room_id': room_id}
    return render(request, 'room.html', context)


def login_view(request):
    return render(request, 'login.html')


def register_view(request):
    return render(request, 'register.html')
