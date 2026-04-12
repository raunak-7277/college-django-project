from django.shortcuts import render
# Create your views here.
from django.shortcuts import render


def home(request):
    return render(request, 'home.html')

def create_room(request):
    return render(request, 'create_room.html')    
