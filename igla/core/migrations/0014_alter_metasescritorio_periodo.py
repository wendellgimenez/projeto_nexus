# Generated by Django 5.0.4 on 2024-09-03 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_logentry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metasescritorio',
            name='periodo',
            field=models.DateField(),
        ),
    ]
