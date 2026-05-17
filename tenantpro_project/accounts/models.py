from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin','Platform Admin'),
        ('owner','Property Owner'),
        ('tenant','Tenant'),
        ('society_admin','Society Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    phone = models.CharField(max_length=15, blank=True)
    avatar_initials = models.CharField(max_length=3, blank=True)
    profile_photo = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.avatar_initials:
            name = self.get_full_name() or self.username
            parts = name.split()
            self.avatar_initials = ''.join(p[0].upper() for p in parts[:2])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
