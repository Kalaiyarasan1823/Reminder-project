from django.db import models
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from dateutil.relativedelta import relativedelta

class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.URLField(max_length=500)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Push subscription for {self.user.username}"
    
    class Meta:
        unique_together = ['user', 'endpoint']

class Category(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color code
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['name', 'user']

class Reminder(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    REPEAT_CHOICES = [
        ('none', 'No Repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField(default=date.today)  
    time = models.TimeField(default=time(12, 0))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Recurring fields
    repeat_type = models.CharField(max_length=10, choices=REPEAT_CHOICES, default='none')
    next_due_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
   
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Set next_due_date when creating or updating
        if not self.next_due_date:
            self.next_due_date = self.date
        super().save(*args, **kwargs)
    
    def get_next_due_date(self):
        """Calculate the next due date based on repeat type"""
        if not self.is_recurring or self.repeat_type == 'none':
            return self.date
        
        current_date = self.next_due_date or self.date
        
        if self.repeat_type == 'daily':
            return current_date + timedelta(days=1)
        elif self.repeat_type == 'weekly':
            return current_date + timedelta(weeks=1)
        elif self.repeat_type == 'monthly':
            return current_date + relativedelta(months=1)
        elif self.repeat_type == 'yearly':
            return current_date + relativedelta(years=1)
        
        return current_date
    
    def advance_to_next(self):
        """Move to the next occurrence of this recurring reminder"""
        if self.is_recurring and self.repeat_type != 'none':
            self.next_due_date = self.get_next_due_date()
            self.completed = False
            self.save()
    
    class Meta:
        ordering = ['-priority', 'date', 'time']
