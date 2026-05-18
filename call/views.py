import uuid
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .models import Meeting, Staff, User


# Gets the current normal user from the URL or form data.
def get_user(request):
    username = request.GET.get('user') or request.POST.get('user')
    return User.objects.filter(username=username).first() if username else None


# Shows the home page.
def home(request):
    return render(request, 'home.html', {'user': get_user(request)})


# Creates a new meeting room for a logged-in user.
def create_room(request):
    user = get_user(request)

    if not user:
        return redirect('login')

    room_id = str(uuid.uuid4())[:8]
    Meeting.objects.create(
        creator=user,
        meeting_code=room_id,
        is_premium=user.is_paid,
    )

    return redirect(f'/room/{room_id}/?user={user.username}')


# Opens an existing meeting room.
def room(request, room_id):
    user = get_user(request)

    if not user:
        return redirect('login')

    meeting = Meeting.objects.filter(meeting_code=room_id).first()

    if not meeting:
        return redirect(f'/dashboard/?user={user.username}')

    return render(request, 'room.html', {
        'room_id': room_id,
        'user': user,
        'meeting_created_at': meeting.created_at.timestamp(),
        'is_premium_room': meeting.is_premium,
    })


# Lets a logged-in user join a room using a room code.
def join_room(request):
    user = get_user(request)

    if not user:
        return redirect('login')

    if request.method == 'POST':
        room_id = request.POST.get('room_id', '').strip()
        if room_id:
            return redirect(f'/room/{room_id}/?user={user.username}')
        return render(request, 'join_room.html', {
            'error': 'Please enter a room ID.',
            'user': user,
        })

    return render(request, 'join_room.html', {'user': user})


# Handles user, staff, and admin login from the same login page.
def login_view(request):
    if request.method != 'POST':
        return render(request, 'login.html', {'selected_role': 'user'})

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    role = request.POST.get('role', 'user').strip()

    if not username or not password:
        return render(request, 'login.html', {
            'error': 'Username and password are required.',
            'selected_role': role,
        })

    if role == 'admin':
        admin_user = authenticate(request, username=username, password=password)
        if admin_user and admin_user.is_superuser:
            auth_login(request, admin_user)
            return redirect('/admin/')
        return render(request, 'login.html', {
            'error': 'Admin username or password is incorrect.',
            'selected_role': role,
        })

    if role == 'staff':
        staff = Staff.objects.filter(
            username=username,
            password=password,
            is_active=True,
        ).first()
        if staff:
            request.session['staff_id'] = staff.id
            return redirect('staff_dashboard')
        return render(request, 'login.html', {
            'error': 'Staff username or password is incorrect.',
            'selected_role': role,
        })

    user = User.objects.filter(username=username, password=password).first()

    if user:
        return redirect(f'/dashboard/?user={user.username}')

    return render(request, 'login.html', {
        'error': 'Invalid username or password. Please try again.',
        'selected_role': role,
    })


# Registers a new normal user account.
def register_view(request):
    if request.method != 'POST':
        return render(request, 'register.html')

    name = request.POST.get('name', '').strip()
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    confirm = request.POST.get('confirm_password', '').strip()

    if not name or not username or not password:
        error = 'All fields are required.'
    elif len(username) < 3:
        error = 'Username must be at least 3 characters.'
    elif len(password) < 4:
        error = 'Password must be at least 4 characters.'
    elif password != confirm:
        error = 'Passwords do not match.'
    elif User.objects.filter(username=username).exists():
        error = 'Username already taken. Please choose another.'
    else:
        User.objects.create(
            name=name,
            username=username,
            password=password,
            is_paid=False,
        )
        return redirect('login')

    return render(request, 'register.html', {
        'error': error,
        'name': name,
        'username': username,
    })


# Logs out staff/admin sessions and returns to home.
def logout_view(request):
    request.session.pop('staff_id', None)
    auth_logout(request)
    return redirect('home')


# Shows staff dashboard with user and membership details.
def staff_dashboard(request):
    staff_id = request.session.get('staff_id')
    staff = Staff.objects.filter(id=staff_id, is_active=True).first()

    if not staff:
        return redirect('login')

    app_users = User.objects.all().order_by('name', 'username')
    total_users = app_users.count()
    paid_users = app_users.filter(is_paid=True).count()

    return render(request, 'staff_dashboard.html', {
        'user': None,
        'staff_user': staff,
        'app_users': app_users,
        'total_users': total_users,
        'paid_users': paid_users,
        'free_users': total_users - paid_users,
    })


# Shows the normal user dashboard after login.
def dashboard(request):
    user = get_user(request)

    if not user:
        return redirect('login')

    return render(request, 'dashboard.html', {'user': user})


# Shows all meetings created by the current user.
def meeting_history(request):
    user = get_user(request)

    if not user:
        return redirect('login')

    meetings = Meeting.objects.filter(creator=user).order_by('-created_at')

    return render(request, 'meeting_history.html', {
        'user': user,
        'meetings': meetings,
    })


# Saves the ending time of a meeting.
def end_meeting(request, room_id):
    user = get_user(request)
    meeting = Meeting.objects.filter(meeting_code=room_id).first()

    if request.method == 'POST' and user and meeting:
        meeting.end_meeting()

    return JsonResponse({'ok': True})


# Shows the subscription page for unpaid users.
def subscription_page(request):
    user = get_user(request)

    if not user:
        return redirect('login')

    if user.is_paid:
        return redirect(f'/dashboard/?user={user.username}')

    return render(request, 'subscription.html', {'user': user})
