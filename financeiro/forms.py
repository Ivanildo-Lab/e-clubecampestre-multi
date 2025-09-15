# financeiro/forms.py

from django import forms
# A importação agora vem do lugar certo: o arquivo de modelos!
from .models import Mensalidade 

class MensalidadeForm(forms.ModelForm):
    class Meta:
        model = Mensalidade
        fields = ['valor', 'data_vencimento', 'data_pagamento', 'status']
        widgets = {
            'data_vencimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_pagamento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'