# Generated by Django 5.0.4 on 2024-08-28 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_escritorio'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatrizReceitas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relatorio_xp', models.CharField(max_length=255)),
                ('produtos_categoria', models.CharField(max_length=255)),
                ('linha_receita', models.CharField(max_length=255)),
                ('classe_ativo', models.CharField(max_length=255)),
                ('subclasse_ativo', models.CharField(max_length=255)),
                ('receita_comissoes', models.DecimalField(decimal_places=2, max_digits=12)),
                ('receita_ai', models.DecimalField(decimal_places=2, max_digits=12)),
                ('receita_escritorio', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
    ]