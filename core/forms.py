from django import forms
from .models import ConfiguracaoSistema

class ConfiguracaoSistemaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = ['valor', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'style': 'resize:none;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # O campo chave não é editável, mas vamos mostrá-lo como título no template
        # O valor deve ter uma ajuda visual
        if self.instance.chave == 'CAIXA_PADRAO_ID':
             self.fields['valor'].help_text = "Insira o ID do Caixa (Veja o número na lista de Caixas)."
             