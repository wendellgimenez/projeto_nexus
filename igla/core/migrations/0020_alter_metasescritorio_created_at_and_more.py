# Generated by Django 5.0.4 on 2024-09-04 15:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_metasescritorio_updated_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='metasescritorio',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='metasescritorio',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metas_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='metasescritorio',
            name='meta_nps',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='metasescritorio',
            name='meta_roa',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='metasescritorio',
            name='periodo',
            field=models.CharField(max_length=7),
        ),
        migrations.AlterField(
            model_name='metasescritorio',
            name='updated_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metas_updated', to=settings.AUTH_USER_MODEL),
        ),
    ]
