from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def home(request):
    return render(request, 'IDS/home.html')

def about_us(request):
    return render(request, 'IDS/about_us.html')

def contact_us(request):
    return render(request, 'IDS/contact_us.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    return render(request, 'IDS/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'IDS/login.html')

@login_required
def dashboard(request):
    return render(request, 'IDS/dashboard.html')

@login_required
def file_upload(request):
    return render(request, 'IDS/file_upload.html')

@login_required
def analysis_report(request):
    return render(request, 'IDS/analysis_report.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')