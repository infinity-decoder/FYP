from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'IDS/home.html')

def about_us(request):
    return render(request, 'IDS/about_us.html')

def contact_us(request):
    return render(request, 'IDS/contact_us.html')

def register(request):
    if request.method == 'POST':
        # Simulate registration logic
        return redirect('login')
    return render(request, 'IDS/register.html')

def user_login(request):
    if request.method == 'POST':
        # Simulate login logic
        return redirect('dashboard')
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
    return redirect('home')