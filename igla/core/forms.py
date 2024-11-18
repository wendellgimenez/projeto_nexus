# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import psycopg2
from .models import Profile, Escritorio, MatrizReceitas, MetasEscritorio

class CustomUserCreationForm(forms.ModelForm):
    name = forms.ChoiceField(choices=[], label='Nome')
    email = forms.EmailField(required=True, label='E-mail', widget=forms.EmailInput(attrs={'readonly': 'readonly'}))
    department = forms.CharField(required=False, label='Departamento', widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    user_level = forms.ChoiceField(choices=Profile.USER_LEVEL_CHOICES, label='Nível de Usuário')

    class Meta:
        model = User
        fields = ('name', 'email', 'department', 'user_level')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['name'].choices = self.get_names_choices()
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'id': 'name-select'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'id': 'email-field'})
        self.fields['department'].widget.attrs.update({'class': 'form-control', 'id': 'department-field'})
        self.fields['name'].initial = 'Selecione um Usuário'
        self.fields['user_level'].widget.attrs.update({'class': 'form-control'})

    def get_names_choices(self):
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor()
        cursor.execute("SELECT nome_ai FROM dados_assessoria.d_assessores WHERE username like '%@liberta.com.vc' and demissao is null and departamento is not null and departamento != 'Não Comercial'")
        names = cursor.fetchall()
        cursor.close()
        conn.close()
        choices = [('Selecione um Usuário', 'Selecione um Usuário')] + [(name[0], name[0]) for name in names]
        return choices

class EscritorioForm(forms.ModelForm):
    class Meta:
        model = Escritorio
        fields = ['codigo', 'nome', 'ir']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ir': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EscritorioForm, self).__init__(*args, **kwargs)
        # Tornando campos obrigatórios conforme necessidade de cadastro/edição
        self.fields['codigo'].required = True
        self.fields['nome'].required = True
        self.fields['ir'].required = True


class MatrizReceitasForm(forms.ModelForm):
    class Meta:
        model = MatrizReceitas
        fields = '__all__'

class MetasEscritorioForm(forms.ModelForm):
    periodo = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: jan/2024', 'class': 'form-control', 'style': 'max-width: 200px;'}),
        label='Período (Digite como o exemplo: jan/2024)'
    )
    meta_roa = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Ex: 0,80', 'class': 'form-control', 'style': 'max-width: 100px;'}),
        label='Meta ROA'
    )
    meta_nps = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Ex: 90,0', 'class': 'form-control', 'style': 'max-width: 100px;'}),
        label='Meta NPS'
    )

    class Meta:
        model = MetasEscritorio
        fields = ['periodo', 'meta_roa', 'meta_nps']
        widgets = {
            'periodo': forms.TextInput(attrs={'placeholder': 'Ex: jan/2024'}),
            'meta_roa': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'meta_nps': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }