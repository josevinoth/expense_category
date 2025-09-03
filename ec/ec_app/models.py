from django.db import models
from django.contrib.auth.models import User

class BankStatementUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    narration = models.TextField()
    withdrawal = models.FloatField(null=True, blank=True)
    deposit = models.FloatField(null=True, blank=True)
    balance = models.FloatField(null=True, blank=True)
    predicted_category = models.CharField(max_length=100, blank=True)
    actual_category = models.CharField(max_length=100, blank=True)
