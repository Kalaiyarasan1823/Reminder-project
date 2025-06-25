from django.core.management.base import BaseCommand
from django.utils import timezone
from Reminder_app.models import Reminder
from Reminder_app.views import send_push_notification
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Send push notifications for due reminders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=15,
            help='Send notifications for reminders due within this many minutes (default: 15)'
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        now = timezone.now()
        due_time = now + timedelta(minutes=minutes)
        
        # Get reminders due within the specified time window
        due_reminders = Reminder.objects.filter(
            completed=False,
            date__lte=due_time.date(),
            time__lte=due_time.time()
        ).select_related('user', 'category')
        
        sent_count = 0
        
        for reminder in due_reminders:
            try:
                # Send push notification
                title = f"Reminder: {reminder.title}"
                body = f"Due: {reminder.date} at {reminder.time}"
                
                if reminder.description:
                    body += f"\n{reminder.description[:100]}..."
                
                if reminder.category:
                    body += f"\nCategory: {reminder.category.name}"
                
                send_push_notification(
                    user=reminder.user,
                    title=title,
                    body=body,
                    data={
                        'type': 'reminder',
                        'reminder_id': reminder.id,
                        'priority': reminder.priority
                    }
                )
                
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Sent notification for reminder "{reminder.title}" to {reminder.user.username}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to send notification for reminder "{reminder.title}": {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully sent {sent_count} push notifications'
            )
        ) 