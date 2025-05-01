# webapp/IDS/models.py

from django.db import models
from django.contrib.auth.models import User

class PcapFile(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    PROGRESS_STAGES = [
        ('uploaded', 'File Uploaded'),
        ('converting', 'Converting PCAP to CSV'),
        ('preprocessing', 'Preprocessing Data'),
        ('predicting', 'Running Predictions'),
        ('saving', 'Saving Results'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    progress_stage = models.CharField(
        max_length=20, 
        choices=PROGRESS_STAGES, 
        default='uploaded'
    )
    progress_message = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        default='File uploaded successfully'
    )
    analysis_result = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

    def filename(self):
        return self.file.name.split('/')[-1]

    def update_progress(self, stage, message):
        self.progress_stage = stage
        self.progress_message = message
        self.save()


class AnalysisResult(models.Model):
    pcap_file = models.OneToOneField(PcapFile, on_delete=models.CASCADE, related_name='detailed_report')
    total_packets = models.IntegerField()
    malicious_count = models.IntegerField()
    normal_count = models.IntegerField()
    malicious_ips = models.JSONField(default=list, blank=True)
    model_details = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.pcap_file.filename()}"