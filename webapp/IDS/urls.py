# webapp/IDS/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # General pages
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Core functionality
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.file_upload, name='file_upload'),

    # PCAP analysis workflow
    path('analyze/<int:file_id>/', views.analyze_pcap, name='analyze_pcap'),
    path('report/<int:file_id>/', views.analysis_report, name='analysis_report'),
    path('download_report_pdf/<int:file_id>/', views.download_report_pdf, name='download_report_pdf'),
]
