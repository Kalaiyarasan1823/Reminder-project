from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, ReminderForm
from .models import Reminder

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful.")
            return redirect('reminder_list')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Login successful.")
            return redirect('reminder_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required
def reminder_list(request):
    reminders = Reminder.objects.filter(user=request.user)
    return render(request, 'reminder_list.html', {'reminders': reminders})

@login_required
def add_reminder(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            return redirect('reminder_list')
    else:
        form = ReminderForm()
    return render(request, 'add_reminder.html', {'form': form})

@login_required
def edit_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            return redirect('reminder_list')
    else:
        form = ReminderForm(instance=reminder)
    return render(request, 'edit_reminder.html', {'form': form})

@login_required
def delete_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        reminder.delete()
        return redirect('reminder_list')
    return render(request, 'delete_reminder.html', {'reminder': reminder})