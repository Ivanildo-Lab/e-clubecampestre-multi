# socios/forms.py

from django import forms
from core.models import Socio, CategoriaSocio, Convenio, Dependente
from django.forms import inlineformset_factory
from core.models import Convenio 

# Em socios/forms.py

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = [
            'nome', 'apelido', 'foto', 'data_nascimento', 'cpf', 'rg',
            'nacionalidade', 'naturalidade', 'estado_civil', 'profissao', 
            'nome_pai', 'nome_mae', 'email', 'tel_residencial', 'tel_trabalho',
            'endereco', 'bairro', 'cidade', 'estado', 'cep',
            'categoria', 'convenio', 'num_registro', 'num_contrato',
            'data_admissao', 'situacao', 'observacoes',
        ]
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_admissao': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 4, 'style': 'resize: none;'}),
        }

    def __init__(self, *args, **kwargs):
        # REMOVEMOS a lógica de 'empresa = kwargs.pop...' 
        super().__init__(*args, **kwargs)
        
        # Auto numeração: num_registro = último id + 1 para novos
        if not self.instance.pk and not self.initial.get('num_registro') and not self.data.get('num_registro'):
            try:
                from core.models import Socio as SocioModel
                ultimo = SocioModel.objects.order_by('-id').first()
                proximo = (ultimo.id + 1) if ultimo else 1
                # Garante que não colida com num_registro existente
                while SocioModel.objects.filter(num_registro=proximo).exists():
                    proximo += 1
                self.fields['num_registro'].initial = proximo
                self.fields['num_registro'].help_text = f"Próximo disponível: {proximo} (id do último sócio +1)"
            except:
                pass

        # A única responsabilidade deste __init__ é estilizar os campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['foto'].widget.attrs.pop('class', None)
        # Destaca num_registro como auto
        if 'num_registro' in self.fields:
            self.fields['num_registro'].widget.attrs['placeholder'] = 'Gerado automaticamente'

        
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

class CategoriaSocioForm(forms.ModelForm):
    class Meta:
        model = CategoriaSocio
        fields = ['nome', 'descricao', 'valor_mensalidade', 'dia_vencimento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ConvenioForm(forms.ModelForm):
    class Meta:
        model = Convenio
        fields = ['nome', 'empresa_contato', 'telefone_contato', 'valor_mensalidade', 'dia_vencimento']
        widgets = {
            'empresa_contato': forms.TextInput(attrs={'placeholder': 'Nome do contato na empresa'}),
            'telefone_contato': forms.TextInput(attrs={'placeholder': '(XX) XXXXX-XXXX'}),
            'valor_mensalidade': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'dia_vencimento': forms.NumberInput(attrs={'min': '0', 'max': '31', 'placeholder': '10'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
