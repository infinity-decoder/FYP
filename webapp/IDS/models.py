from django.db import models
from django.contrib.auth.models import User

class PcapFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='pcaps/')
    uploaded_at = models.DateTimeField(auto_now_add=True)