from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'), 
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reminders/', views.reminder_list, name='reminder_list'),
    path('add/', views.add_reminder, name='add_reminder'),
    path('edit/<int:pk>/', views.edit_reminder, name='edit_reminder'),
    path('delete/<int:pk>/', views.delete_reminder, name='delete_reminder'),
]
