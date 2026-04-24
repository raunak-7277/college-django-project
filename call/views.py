import uuid
from django.shortcuts import render, redirect
from .models import User, Meeting


# ─────────────────────────────────────────────
#  HELPER: get logged-in user from URL param
# ─────────────────────────────────────────────
def get_logged_in_user(request):
    username = request.GET.get('user')
    if not username:
        return None
    return User.objects.filter(username=username).first()


# ─────────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────────
def home(request):
    user = get_logged_in_user(request)
    return render(request, 'home.html', {'user': user})


# ─────────────────────────────────────────────
#  CREATE ROOM
# ─────────────────────────────────────────────
def create_room(request):
    # Must be logged in to create a room
    username = request.GET.get('user')
    user = User.objects.filter(username=username).first() if username else None

    if not user:
        # Not logged in → redirect to login
        return redirect('login')

    # Generate a random 8-character room code
    room_id = str(uuid.uuid4())[:8]

    # Save meeting to database
    Meeting.objects.create(
        user=user,
        meeting_code=room_id
    )

    # Redirect to the room, carrying the username in URL
    return redirect(f'/room/{room_id}/?user={username}')


# ─────────────────────────────────────────────
#  ROOM PAGE
# ─────────────────────────────────────────────
def room(request, room_id):
    # Must be logged in to join a room
    username = request.GET.get('user')
    user = User.objects.filter(username=username).first() if username else None

    if not user:
        return redirect('login')

    return render(request, 'room.html', {
        'room_id': room_id,
        'user': user
    })


# ─────────────────────────────────────────────
#  JOIN ROOM (from home page form)
# ─────────────────────────────────────────────
def join_room(request):
    username = request.GET.get('user')
    user = User.objects.filter(username=username).first() if username else None

    if not user:
        return redirect('login')

    if request.method == 'POST':
        room_id = request.POST.get('room_id', '').strip()
        if room_id:
            return redirect(f'/room/{room_id}/?user={username}')
        return render(request, 'join_room.html', {
            'error': 'Please enter a room ID.',
            'user': user
        })

    return render(request, 'join_room.html', {'user': user})


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Basic validation: fields must not be empty
        if not username or not password:
            return render(request, 'login.html', {
                'error': 'Username and password are required.'
            })

        # Check if user exists with matching credentials
        user = User.objects.filter(username=username, password=password).first()

        if user:
            # Login success → go to dashboard, carry username in URL
            return redirect(f'/dashboard/?user={username}')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password. Please try again.'
            })

    return render(request, 'login.html')


# ─────────────────────────────────────────────
#  REGISTER
# ─────────────────────────────────────────────
def register_view(request):
    if request.method == 'POST':
        name     = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm  = request.POST.get('confirm_password', '').strip()

        # --- Validations ---
        if not name or not username or not password:
            return render(request, 'register.html', {
                'error': 'All fields are required.'
            })

        if len(username) < 3:
            return render(request, 'register.html', {
                'error': 'Username must be at least 3 characters.',
                'name': name, 'username': username
            })

        if len(password) < 4:
            return render(request, 'register.html', {
                'error': 'Password must be at least 4 characters.',
                'name': name, 'username': username
            })

        if password != confirm:
            return render(request, 'register.html', {
                'error': 'Passwords do not match.',
                'name': name, 'username': username
            })

        # Check duplicate username
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already taken. Please choose another.',
                'name': name
            })

        # Save the new user
        User.objects.create(
            name=name,
            username=username,
            password=password  # plain text (fine for college project)
        )

        # Registration success → go to login
        return redirect('login')

    return render(request, 'register.html')


# ─────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────
def logout_view(request):
    # Simply redirect to home (no session to clear)
    return redirect('home')


# ─────────────────────────────────────────────
#  DASHBOARD (after login)
# ─────────────────────────────────────────────
def dashboard(request):
    username = request.GET.get('user')
    user = User.objects.filter(username=username).first() if username else None

    if not user:
        return redirect('login')

    return render(request, 'dashboard.html', {'user': user})


# ─────────────────────────────────────────────
#  MEETING HISTORY
# ─────────────────────────────────────────────
def meeting_history(request):
    username = request.GET.get('user')
    user = User.objects.filter(username=username).first() if username else None

    if not user:
        return redirect('login')

    # Get all meetings for this user, newest first
    meetings = Meeting.objects.filter(user=user).order_by('-date')

    return render(request, 'meeting_history.html', {
        'user': user,
        'meetings': meetings
    })