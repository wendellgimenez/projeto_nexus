# Generated by Django 5.0.4 on 2024-08-26 18:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('department', models.CharField(choices=[('Gerencial Assessoria', 'Gerencial Assessoria'), ('Assessoria Comercial', 'Assessoria Comercial'), ('Renda Variável', 'Renda Variável'), ('Alocação/Produtos', 'Alocação/Produtos'), ('Academia Liberta', 'Academia Liberta'), ('Seguridade', 'Seguridade'), ('Atendimento Digital', 'Atendimento Digital'), ('Liberta Wealth', 'Liberta Wealth'), ('PJ/Crédito/Câmbio', 'PJ/Crédito/Câmbio'), ('Gestão de Pessoas', 'Gestão de Pessoas')], max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]