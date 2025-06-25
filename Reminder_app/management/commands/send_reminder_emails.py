from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from Reminder_app.models import Reminder
from django.contrib.auth.models import User
from django.conf import settings

class Command(BaseCommand):
    help = 'Send reminder emails for reminders due in the next 24 hours.'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        tomorrow = now + timezone.timedelta(days=1)
        reminders = Reminder.objects.filter(
            completed=False,
            date__range=[now.date(), tomorrow.date()]
        )
        users = User.objects.filter(reminder__in=reminders).distinct()
        site_url = 'http://127.0.0.1:8000'  # Change to your production URL if needed

        for user in users:
            user_reminders = reminders.filter(user=user)
            for reminder in user_reminders:
                subject = f"Reminder: {reminder.title} is due soon!"
                html_content = render_to_string(
                    'email/reminder_notification.html',
                    {
                        'user': user,
                        'reminder': reminder,
                        'site_url': site_url,
                    }
                )
                email = EmailMultiAlternatives(
                    subject,
                    html_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                self.stdout.write(self.style.SUCCESS(f"Sent reminder email to {user.email} for '{reminder.title}'"))
        self.stdout.write(self.style.SUCCESS('All due reminder emails sent.')) 