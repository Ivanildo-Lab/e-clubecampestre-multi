from django import forms
from .models import Venda
from core.models import Socio
from financeiro.models import Caixa
from formas_pagamento.models import FormaPagamento
from estoque.models import Produto


class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['tipo', 'forma_pagamento', 'caixa', 'socio', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Observacao opcional...'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['forma_pagamento'].queryset = FormaPagamento.objects.filter(empresa=empresa, ativo=True)
            self.fields['caixa'].queryset = Caixa.objects.filter(empresa=empresa)
            self.fields['socio'].queryset = Socio.objects.filter(empresa=empresa, situacao='ATIVO').order_by('nome')
        self.fields['forma_pagamento'].required = False
        self.fields['caixa'].required = False
        self.fields['socio'].required = False
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')
        caixa = cleaned.get('caixa')
        socio = cleaned.get('socio')
        if tipo == 'A_VISTA':
            if not caixa:
                raise forms.ValidationError('Para venda a vista, selecione o caixa.')
        elif tipo == 'A_PRAZO':
            if not socio:
                raise forms.ValidationError('Para venda a prazo, selecione o socio.')
        return cleaned
