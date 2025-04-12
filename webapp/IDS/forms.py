from django import forms
from .models import PcapFile

class PcapUploadForm(forms.ModelForm):
    class Meta:
        model = PcapFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': '.pcap,.pcapng',
                'class': 'form-control'
            })
        }