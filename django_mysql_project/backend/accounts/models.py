from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_username = models.CharField(max_length=100, blank=True)
    github_token = models.CharField(max_length=255, blank=True)  # OAuth2 Access Token 저장

    def __str__(self):
        return f"{self.user.username} - GitHub"
