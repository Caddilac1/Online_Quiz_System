# Generated by Django 5.2.3 on 2025-06-23 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('System', '0004_sheettask_shared_with'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='option_c',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='option_d',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='tag',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
