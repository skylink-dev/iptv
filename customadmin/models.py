# customadmin/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('partner', 'Partner'),
        ('accounts_and_auditing ', 'Accounts and Auditing'),
        ('developer ', 'Developer'),
        
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="partner")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
