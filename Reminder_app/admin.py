from django.contrib import admin
from .models import Reminder, Category, PushSubscription

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'date', 'time', 'priority', 'completed', 'category', 'is_recurring']
    list_filter = ['priority', 'completed', 'is_recurring', 'category', 'date']
    search_fields = ['title', 'description', 'user__username']
    date_hierarchy = 'date'
    list_editable = ['completed', 'priority']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'user__username']

@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'endpoint', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'endpoint']
    readonly_fields = ['created_at']

