# Generated by Django 5.0.4 on 2024-09-11 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_alter_metasescritorio_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matrizreceitas',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]