from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('userpanel:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('userpanel:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'userpanel/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('userpanel:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not password or not confirm_password or not email:
            messages.error(request, 'All fields are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('userpanel:login')

    return render(request, 'userpanel/register.html')


@login_required
def dashboard_view(request):
    return render(request, 'userpanel/dashboard.html', {
        'user': request.user
    })


def logout_view(request):
    logout(request)
    return redirect('userpanel:login')
