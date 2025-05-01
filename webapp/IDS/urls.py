# webapp/IDS/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.file_upload, name='file_upload'),
    path('analyze/<int:file_id>/', views.analyze_pcap, name='analyze_pcap'),
    path('report/<int:file_id>/', views.analysis_report, name='analysis_report'),
    path('report/<int:file_id>/pdf/', views.download_report_pdf, name='download_report_pdf'),
    # Add this new URL pattern:
    path('api/progress/<int:file_id>/', views.get_analysis_progress, name='get_analysis_progress'),
]