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
      if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username=username, password=password).first()

        if user:
            return redirect("home")  
        else:
            return render(request, "login.html", {"error": "Invalid"})


def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        User.objects.create(
            name=name,
            username=username,
            password=password
        )

        return redirect("login")

    return render(request, "register.html")
