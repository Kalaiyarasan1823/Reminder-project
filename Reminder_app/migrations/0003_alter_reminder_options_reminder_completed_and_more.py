# Generated by Django 5.2 on 2025-06-21 09:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reminder_app', '0002_remove_reminder_created_at_remove_reminder_due_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reminder',
            options={'ordering': ['-priority', 'date', 'time']},
        ),
        migrations.AddField(
            model_name='reminder',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reminder',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reminder',
            name='priority',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=10),
        ),
    ]
