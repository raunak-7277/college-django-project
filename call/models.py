from django.db import models

from django.db import models

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

    def __str__(self):
        return self.username

class Meeting(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    meeting_code = models.CharField(max_length=100)

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.meeting_code        
