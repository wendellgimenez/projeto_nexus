# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    USER_LEVEL_CHOICES = [
        ('Master', 'Master'),
        ('Gerencial', 'Gerencial'),
        ('Administrador', 'Administrador'),
        ('Visualizador', 'Visualizador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=255, blank=True, null=True)
    user_level = models.CharField(
        max_length=20,
        choices=USER_LEVEL_CHOICES,
        default='Visualizador',
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)  # Adiciona data de criação com valor padrão

    def __str__(self):
        return self.user.username

class Escritorio(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=255)
    ir = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome
    
class MatrizReceitas(models.Model):
    data_referencia = models.DateField()
    relatorio_xp = models.CharField(max_length=255)
    produto_categoria = models.CharField(max_length=255)
    linha_de_receita = models.CharField(max_length=255)
    classe_do_ativo = models.CharField(max_length=255)
    subclasse_do_ativo = models.CharField(max_length=255)
    receita_comissoes = models.CharField(max_length=255)
    receita_ai = models.CharField(max_length=255)
    receita_escritorio = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'dev_igla.linha_de_receita'  # Nome completo com schema
        managed = True

    def __str__(self):
        return f"{self.relatorio_xp} - {self.produto_categoria}"
    
class MetasEscritorio(models.Model):
    periodo = models.CharField(max_length=8)  # Formato: "jun/2024"
    meta_roa = models.DecimalField(max_digits=5, decimal_places=2)  # Porcentagem como decimal: exemplo 0.80
    meta_nps = models.DecimalField(max_digits=5, decimal_places=2)  # Porcentagem como decimal: exemplo 90.00
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='metas_criadas')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='metas_atualizadas')  # Novo campo

    def __str__(self):
        return f"Período: {self.periodo} - ROA: {self.meta_roa}%, NPS: {self.meta_nps}%"
    
class LogEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_log_entries')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user} - {self.action} at {self.timestamp}'