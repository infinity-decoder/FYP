from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import PcapFile
from .forms import PcapUploadForm

def home(request):
    """Render the home page for non-authenticated users"""
    return render(request, 'IDS/home.html')

def about_us(request):
    """Render the about us page"""
    return render(request, 'IDS/about_us.html')

def contact_us(request):
    """Render the contact us page"""
    return render(request, 'IDS/contact_us.html')

def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    return render(request, 'IDS/register.html', {'form': form})

def user_login(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'IDS/login.html')

@login_required
def dashboard(request):
    """Render user dashboard"""
    return render(request, 'IDS/dashboard.html')

@login_required
def file_upload(request):
    """Handle PCAP file uploads"""
    if request.method == 'POST':
        form = PcapUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pcap_file = form.save(commit=False)
                pcap_file.user = request.user
                pcap_file.status = 'uploaded'
                pcap_file.save()
                messages.success(request, 'PCAP file uploaded successfully!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Invalid file format (.pcap or .pcapng only)')
    else:
        form = PcapUploadForm()
    return render(request, 'IDS/file_upload.html', {'form': form})

@login_required
def analysis_report(request, file_id):
    """View analysis report for a specific file"""
    file = get_object_or_404(PcapFile, id=file_id, user=request.user)
    
    # Initialize empty result if none exists
    if not file.analysis_result:
        file.analysis_result = {
            'status': 'pending',
            'malicious_count': 0,
            'normal_count': 0,
            'total_packets': 0
        }
        file.save()
    
    return render(request, 'IDS/analysis_report.html', {
        'file': file,
        'report': file.analysis_result
    })

def user_logout(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')