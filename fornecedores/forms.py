from django import forms
from .models import Fornecedor

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            'nome', 'nome_fantasia', 'cpf_cnpj', 
            'telefone', 'email', 'responsavel',
            'endereco', 'cidade', 'estado', 'observacoes'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3, 'style': 'resize: none;'}),
        }

    def __init__(self, *args, **kwargs):
        # Removemos o argumento 'empresa' do kwargs antes de chamar o super
        # pois o ModelForm não espera receber 'empresa' no init padrão,
        # nós vamos lidar com a empresa na View.
        self.empresa = kwargs.pop('empresa', None) 
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            