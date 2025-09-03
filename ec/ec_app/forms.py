from django import forms
from .models import BankStatementUpload

class UploadForm(forms.ModelForm):
    class Meta:
        model = BankStatementUpload
        fields = ['file']   # Only upload the file
