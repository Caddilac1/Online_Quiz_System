# Generated by Django 5.2.3 on 2025-07-07 23:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('System', '0008_studentprofile_programme'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizattempt',
            name='started_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
