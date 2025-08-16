from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    sign_name = models.CharField(max_length=50)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    practice_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.sign_name}"

class Subscription(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('advanced', 'Advanced'),
        ('pro', 'Pro'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"
    
    def is_valid(self):
        if self.plan == 'free':
            return True
        if not self.is_active:
            return False
        if self.end_date and self.end_date < timezone.now():
            self.is_active = False
            self.save()
            return False
        return True