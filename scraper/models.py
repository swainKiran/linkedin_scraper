from django.db import models

# Create your models here.

class MessageData(models.Model):
    email = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    link = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class VisitedMessage(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
