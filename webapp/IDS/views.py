# webapp/IDS/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os

from xhtml2pdf import pisa
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

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    if request.method == 'POST' and 'file' in request.FILES:
        form = PcapUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pcap_file = form.save(commit=False)
            pcap_file.user = request.user
            pcap_file.status = 'uploaded'
            pcap_file.progress_stage = 'uploaded'
            pcap_file.progress_message = 'File uploaded successfully'
            pcap_file.save()

            # Ensure media directories exist
            media_root = os.path.join(settings.BASE_DIR, 'webapp', 'IDS', 'media')
            for dir_name in ['uploads', 'csvs', 'datasets', 'results']:
                os.makedirs(os.path.join(media_root, dir_name), exist_ok=True)

            # Trigger background analyzer
            analyzer = BackgroundAnalyzer(pcap_file.id)
            analyzer.start()

            messages.success(request, 'File uploaded successfully! Analysis started.')
            return redirect('analysis_report', file_id=pcap_file.id)
        else:
            messages.error(request, 'Invalid file format.')

    user_files = PcapFile.objects.filter(user=request.user).order_by('-uploaded_at')
    latest_file = user_files.first()
    
    return render(request, 'IDS/dashboard.html', {
        'user_files': user_files,
        'latest_file': latest_file,
        'upload_in_progress': latest_file and latest_file.status == 'processing',
        'analysis_completed': latest_file and latest_file.status == 'completed'
    })


@login_required
def file_upload(request):
    if request.method == 'POST':
        form = PcapUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pcap_file = form.save(commit=False)
            pcap_file.user = request.user
            pcap_file.status = 'uploaded'
            pcap_file.progress_stage = 'uploaded'
            pcap_file.progress_message = 'File uploaded successfully'
            pcap_file.save()

            # Ensure media directories exist
            media_root = os.path.join(settings.BASE_DIR, 'webapp', 'IDS', 'media')
            for dir_name in ['uploads', 'csvs', 'datasets', 'results']:
                os.makedirs(os.path.join(media_root, dir_name), exist_ok=True)

            # Trigger background analyzer
            analyzer = BackgroundAnalyzer(pcap_file.id)
            analyzer.start()

            messages.success(request, 'File uploaded successfully! Analysis started.')
            return redirect('analysis_report', file_id=pcap_file.id)
        else:
            messages.error(request, 'Invalid file format.')
    else:
        form = PcapUploadForm()
    return render(request, 'IDS/file_upload.html', {'form': form})


@login_required
def analyze_pcap(request, file_id):
    file = get_object_or_404(PcapFile, id=file_id, user=request.user)

    if file.status not in ['processing', 'completed']:
        file.status = 'processing'
        file.progress_stage = 'converting'
        file.progress_message = 'Starting analysis...'
        file.save()

        analyzer = BackgroundAnalyzer(file.id)
        analyzer.start()

        messages.success(request, f"Analysis started for {file.filename()}")
    else:
        messages.warning(request, "This file is already being processed or completed.")

    return redirect('analysis_report', file_id=file.id)


@login_required
def analysis_report(request, file_id):
    file = get_object_or_404(PcapFile, id=file_id, user=request.user)
    detailed_report = None

    try:
        detailed_report = file.detailed_report
    except AnalysisResult.DoesNotExist:
        pass

    return render(request, 'IDS/analysis_report.html', {
        'file': file,
        'report_data': detailed_report,
        'progress_stage': file.progress_stage,
        'progress_message': file.progress_message
    })


@login_required
def download_report_pdf(request, file_id):
    file = get_object_or_404(PcapFile, id=file_id, user=request.user)
    report = file.detailed_report

    template_path = 'IDS/analysis_report_pdf.html'
    context = {'report_data': report, 'file': file}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file.filename()}_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation error", status=500)

    return response


@login_required
def get_analysis_progress(request, file_id):
    file = get_object_or_404(PcapFile, id=file_id, user=request.user)
    return JsonResponse({
        'status': file.status,
        'progress_stage': file.progress_stage,
        'progress_message': file.progress_message
    })