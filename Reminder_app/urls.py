from django.urls import path
from . import views

urlpatterns = [
    path('', views.reminder_list, name='reminder_list'),
    path('add/', views.add_reminder, name='add_reminder'),
    path('edit/<int:pk>/', views.edit_reminder, name='edit_reminder'),
    path('delete/<int:pk>/', views.delete_reminder, name='delete_reminder'),
    path('toggle/<int:pk>/', views.toggle_completion, name='toggle_completion'),
    path('advance/<int:pk>/', views.advance_recurring, name='advance_recurring'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('calendar/events/', views.reminders_calendar_json, name='calendar_events'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    
    # Export/Import URLs
    path('export/', views.export_reminders, name='export_reminders'),
    path('import/', views.import_reminders, name='import_reminders'),
    
    # Push Notification URLs
    path('push/subscribe/', views.subscribe_push, name='subscribe_push'),
    path('push/unsubscribe/', views.unsubscribe_push, name='unsubscribe_push'),
    path('push/test/', views.test_push_notification, name='test_push_notification'),
]
