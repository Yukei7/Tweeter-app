from django.db import models
from django.contrib.auth.models import User


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text="user who creates this tweet")
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
