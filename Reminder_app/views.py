from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .forms import SignUpForm, ReminderForm, CategoryForm
from .models import Reminder, Category, PushSubscription
from django.db import models
import csv
import io
from datetime import datetime
import json
from pywebpush import webpush, WebPushException
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

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
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        reminders = reminders.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        reminders = reminders.filter(priority=priority_filter)
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        reminders = reminders.filter(category_id=category_filter)
    
    # Filter by completion status
    completion_filter = request.GET.get('completed', '')
    if completion_filter == 'completed':
        reminders = reminders.filter(completed=True)
    elif completion_filter == 'pending':
        reminders = reminders.filter(completed=False)
    
    # Sort by different criteria
    sort_by = request.GET.get('sort', 'priority')
    if sort_by == 'date':
        reminders = reminders.order_by('date', 'time')
    elif sort_by == 'created':
        reminders = reminders.order_by('-created_at')
    else:  # default: priority
        reminders = reminders.order_by('-priority', 'date', 'time')
    
    # Get categories for filter dropdown
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'reminders': reminders,
        'categories': categories,
        'search_query': search_query,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'completion_filter': completion_filter,
        'sort_by': sort_by,
    }
    return render(request, 'reminder_list.html', context)

@login_required
def add_reminder(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            
            # Set recurring logic
            if reminder.repeat_type != 'none':
                reminder.is_recurring = True
                reminder.next_due_date = reminder.date
            
            reminder.save()
            return redirect('reminder_list')
    else:
        form = ReminderForm()
        # Filter categories to only show user's categories
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
    return render(request, 'add_reminder.html', {'form': form})

@login_required
def edit_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            reminder = form.save(commit=False)
            
            # Update recurring logic
            if reminder.repeat_type != 'none':
                reminder.is_recurring = True
                if not reminder.next_due_date:
                    reminder.next_due_date = reminder.date
            else:
                reminder.is_recurring = False
            
            reminder.save()
            return redirect('reminder_list')
    else:
        form = ReminderForm(instance=reminder)
        # Filter categories to only show user's categories
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
    return render(request, 'edit_reminder.html', {'form': form})

@login_required
def delete_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        reminder.delete()
        return redirect('reminder_list')
    return render(request, 'delete_reminder.html', {'reminder': reminder})

@login_required
def toggle_completion(request, pk):
    if request.method == 'POST':
        reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
        reminder.completed = not reminder.completed
        reminder.save()
        return JsonResponse({'completed': reminder.completed})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def advance_recurring(request, pk):
    """Advance a recurring reminder to its next occurrence"""
    if request.method == 'POST':
        reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
        if reminder.is_recurring:
            reminder.advance_to_next()
            messages.success(request, f"Reminder '{reminder.title}' advanced to next occurrence.")
        return redirect('reminder_list')
    return redirect('reminder_list')

@login_required
def calendar_view(request):
    return render(request, 'calendar_view.html')

@login_required
def reminders_calendar_json(request):
    reminders = Reminder.objects.filter(user=request.user)
    events = []
    for reminder in reminders:
        events.append({
            'id': reminder.id,
            'title': reminder.title,
            'start': str(reminder.date),
            'end': str(reminder.date),
            'color': '#e74c3c' if reminder.priority == 'high' else ('#f39c12' if reminder.priority == 'medium' else '#27ae60'),
            'completed': reminder.completed,
        })
    return JsonResponse(events, safe=False)

# Category views
@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'category_list.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f"Category '{category.name}' created successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form': form})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f"Category '{category.name}' deleted successfully.")
        return redirect('category_list')
    return render(request, 'delete_category.html', {'category': category})

@login_required
def export_reminders(request):
    """Export user's reminders to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reminders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Date', 'Time', 'Priority', 'Completed', 'Category', 'Repeat Type', 'Created At'])
    
    reminders = Reminder.objects.filter(user=request.user)
    for reminder in reminders:
        writer.writerow([
            reminder.title,
            reminder.description,
            reminder.date,
            reminder.time,
            reminder.priority,
            reminder.completed,
            reminder.category.name if reminder.category else '',
            reminder.repeat_type,
            reminder.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
def import_reminders(request):
    """Import reminders from CSV"""
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Please select a CSV file to import.')
            return redirect('reminder_list')
        
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('reminder_list')
        
        try:
            # Decode the file content
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.reader(io.StringIO(decoded_file))
            next(csv_data)  # Skip header row
            
            imported_count = 0
            for row in csv_data:
                if len(row) >= 6:  # Ensure we have at least the required fields
                    title, description, date_str, time_str, priority, completed = row[:6]
                    
                    # Parse date and time
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                    except ValueError:
                        continue  # Skip invalid date/time
                    
                    # Create reminder
                    reminder = Reminder.objects.create(
                        user=request.user,
                        title=title,
                        description=description,
                        date=date_obj,
                        time=time_obj,
                        priority=priority if priority in ['low', 'medium', 'high'] else 'medium',
                        completed=completed.lower() == 'true' if completed else False,
                        repeat_type=row[7] if len(row) > 7 and row[7] in ['none', 'daily', 'weekly', 'monthly', 'yearly'] else 'none'
                    )
                    
                    # Handle category if present
                    if len(row) > 6 and row[6]:
                        category_name = row[6]
                        category, created = Category.objects.get_or_create(
                            name=category_name,
                            user=request.user,
                            defaults={'color': '#3498db'}
                        )
                        reminder.category = category
                        reminder.save()
                    
                    imported_count += 1
            
            messages.success(request, f'Successfully imported {imported_count} reminders.')
            
        except Exception as e:
            messages.error(request, f'Error importing reminders: {str(e)}')
        
        return redirect('reminder_list')
    
    return render(request, 'import_reminders.html')

@login_required
def subscribe_push(request):
    """Subscribe user to push notifications"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            endpoint = data.get('endpoint')
            p256dh = data.get('keys', {}).get('p256dh')
            auth = data.get('keys', {}).get('auth')
            
            if not all([endpoint, p256dh, auth]):
                return JsonResponse({'error': 'Missing required subscription data'}, status=400)
            
            # Save or update subscription
            subscription, created = PushSubscription.objects.get_or_create(
                user=request.user,
                endpoint=endpoint,
                defaults={'p256dh': p256dh, 'auth': auth}
            )
            
            if not created:
                subscription.p256dh = p256dh
                subscription.auth = auth
                subscription.save()
            
            return JsonResponse({'message': 'Successfully subscribed to push notifications'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def unsubscribe_push(request):
    """Unsubscribe user from push notifications"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            endpoint = data.get('endpoint')
            
            if endpoint:
                PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
                return JsonResponse({'message': 'Successfully unsubscribed from push notifications'})
            else:
                return JsonResponse({'error': 'Missing endpoint'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def send_push_notification(user, title, body, data=None):
    """Send push notification to a user"""
    subscriptions = PushSubscription.objects.filter(user=user)
    
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,
                    'keys': {
                        'p256dh': subscription.p256dh,
                        'auth': subscription.auth
                    }
                },
                data=json.dumps({
                    'title': title,
                    'body': body,
                    'data': data or {}
                }),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    'sub': f'mailto:{settings.VAPID_EMAIL}'
                }
            )
        except WebPushException as e:
            # Remove invalid subscriptions
            if e.response.status_code == 410:
                subscription.delete()
            print(f"Push notification failed: {e}")

@login_required
def test_push_notification(request):
    """Test push notification endpoint"""
    if request.method == 'POST':
        try:
            send_push_notification(
                user=request.user,
                title="Test Notification",
                body="This is a test push notification from your reminder app!",
                data={'type': 'test'}
            )
            return JsonResponse({'message': 'Test notification sent successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)