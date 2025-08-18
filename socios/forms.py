# socios/forms.py

from django import forms
from core.models import Socio,Dependente
from django.forms import inlineformset_factory

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = [
            'nome', 'apelido', 'foto', 'data_nascimento', 'cpf', 'rg',
            'nacionalidade', 'naturalidade', 'estado_civil', 'profissao', 
            'nome_pai', 'nome_mae', 'email', 'tel_residencial', 'tel_trabalho',
            'endereco', 'bairro', 'cidade', 'estado', 'cep',
            'categoria', 'convenio', 'num_registro', 'num_contrato',
            'data_admissao', 
            'situacao', 'observacoes',
        ]
        
        
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_admissao': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 4, 'style': 'resize: none;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        self.fields['foto'].widget.attrs.pop('class', None)

class DependenteForm(forms.ModelForm):
    class Meta:
        model = Dependente
        fields = ('nome', 'data_nascimento', 'parentesco', 'cpf', 'foto')
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['foto'].widget.attrs.pop('class', None)

# Fábrica que cria o conjunto de formulários de dependentes
DependenteFormSet = inlineformset_factory(
    Socio,  # Modelo Pai
    Dependente,  # Modelo Filho
    form=DependenteForm,  # Formulário a ser usado para cada dependente
    extra=1,  # Começa com 1 formulário em branco para adicionar um novo
    can_delete=True,  # Permite marcar dependentes para exclusão
    can_delete_extra=True
)