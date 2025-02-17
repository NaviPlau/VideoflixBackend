from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """
        Return True if the token is valid, False otherwise. A valid token is
        one that has been created within the last 15 minutes.
        """
        return now() < self.created_at + timedelta(minutes=15)
