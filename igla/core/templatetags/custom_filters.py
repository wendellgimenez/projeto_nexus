# Importa o módulo template do Django para criar filtros customizados para templates
from django import template

# Instancia um objeto Library que será utilizado para registrar os filtros customizados
register = template.Library()

# Define um filtro customizado chamado 'multiply' que multiplica dois valores
@register.filter
def multiply(value, arg):
    try:
        # Converte ambos os valores para float e realiza a multiplicação
        return float(value) * float(arg)
    except (ValueError, TypeError):
        # Caso ocorra um erro na conversão ou multiplicação (ex.: valor não numérico), retorna uma string vazia
        return ''

# Define um filtro customizado chamado 'format_percentage' que formata um valor como porcentagem
@register.filter
def format_percentage(value):
    try:
        # Converte o valor para float, multiplica por 100 e formata com duas casas decimais
        return f"{float(value) * 100:.2f}"
    except (ValueError, TypeError):
        # Em caso de erro (ex.: valor não numérico), retorna uma string vazia
        return ''
