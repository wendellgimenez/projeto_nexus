# Generated by Django 5.0.4 on 2024-08-26 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_profile_user_level'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
