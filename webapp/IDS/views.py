from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import PcapFile, AnalysisResult
from .forms import PcapUploadForm
from .utils.background_processor import BackgroundAnalyzer


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
        messages.error(request, 'Invalid username or password.')
    return render(request, 'IDS/login.html')

@login_required
def dashboard(request):
    user_files = PcapFile.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'IDS/dashboard.html', {'user_files': user_files})

@login_required
def file_upload(request):
    if request.method == 'POST':
        form = PcapUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pcap_file = form.save(commit=False)
                pcap_file.user = request.user
                pcap_file.status = 'uploaded'
                pcap_file.save()
                messages.success(request, 'PCAP file uploaded successfully! Analysis will begin shortly.')

                # Start background analysis
                analyzer = BackgroundAnalyzer(pcap_file.id)
                analyzer.start()

                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Invalid file format (.pcap or .pcapng only)')
    else:
        form = PcapUploadForm()
    return render(request, 'IDS/file_upload.html', {'form': form})

@login_required
def analyze_pcap(request, file_id):
    file = get_object_or_404(PcapFile, id=file_id, user=request.user)

    if file.status not in ['processing', 'completed']:
        file.status = 'processing'
        file.save()

        analyzer = BackgroundAnalyzer(file.id)
        analyzer.start()

        messages.success(request, f"Analysis started for {file.file.name}")
    else:
        messages.warning(request, "File is already being processed or completed.")

    return redirect('analysis_report', file_id=file.id)

@login_required
def analysis_report(request, file_id):
    file = get_object_or_404(PcapFile, id=file_id, user=request.user)
    detailed_report = None

    try:
        detailed_report = file.detailed_report  # OneToOne link
    except AnalysisResult.DoesNotExist:
        pass

    return render(request, 'IDS/analysis_report.html', {
        'file': file,
        'report': file.analysis_result,
        'detailed_report': detailed_report
    })

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
