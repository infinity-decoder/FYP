from django.db import models
from django.contrib.auth.models import User

class PcapFile(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='pcaps/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded'
    )
    analysis_result = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

    def filename(self):
        return self.file.name.split('/')[-1]