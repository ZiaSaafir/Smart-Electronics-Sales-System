from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_ROLES = [
        ('admin', 'Administrator'),
        ('cashier', 'Cashier'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='cashier')
    phone = models.CharField(max_length=20, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"