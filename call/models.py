from django.db import models
from django.utils import timezone

class User(models.Model):
    name = models.CharField(max_length=100)

    username = models.CharField(
        max_length=100,
        unique=True
    )

    password = models.CharField(max_length=255)

    token = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    is_paid = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.username

class Meeting(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    meeting_code = models.CharField(max_length=100)

    is_premium = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return self.meeting_code        
