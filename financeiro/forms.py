# financeiro/forms.py

from django import forms
from django_select2.forms import ModelSelect2Widget
from .models import Conta, PlanoDeContas, Socio, Caixa, LancamentoCaixa,Mensalidade 


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


class PlanoDeContasForm(forms.ModelForm):
    class Meta:
        model = PlanoDeContas
        fields = ['codigo', 'nome', 'tipo', 'parent', 'aceita_lancamentos']
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ex: 1.100.001'}),
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Receita de Mensalidades'}),
        }

    def __init__(self, *args, **kwargs):
        # Pega a empresa que a view vai nos passar
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        if empresa:
            # Filtra o campo 'parent' para mostrar apenas contas da mesma empresa
            # e que NÃO aceitam lançamentos (são contas sintéticas/agrupadoras).
            self.fields['parent'].queryset = PlanoDeContas.objects.filter(
                empresa=empresa,
                aceita_lancamentos=False
            )
            self.fields['parent'].empty_label = "Nenhuma (Conta Principal)"

        # Aplica a classe do Bootstrap a todos os campos
        for field_name, field in self.fields.items():
            # Checkboxes são estilizados de forma diferente
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'



class CaixaForm(forms.ModelForm):
    class Meta:
        model = Caixa
        fields = ['nome', 'saldo_inicial']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Caixa da Secretaria, Conta Banco do Brasil'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'




class ContaForm(forms.ModelForm):
    plano_de_contas = forms.ModelChoiceField(
        queryset=PlanoDeContas.objects.all(),
        label="Plano de Contas",
        widget=ModelSelect2Widget(
            model=PlanoDeContas,
            search_fields=['nome__icontains'],
            attrs={
                'data-placeholder': 'Digite para buscar um plano de contas...',
                'data-width': '100%'  # <-- AQUI ESTÁ A CORREÇÃO
            }
        )
    )
        
    socio = forms.ModelChoiceField(
        queryset=Socio.objects.all(),
        label="Sócio (Opcional)",
        required=False,
        widget=ModelSelect2Widget(
            model=Socio,
            search_fields=['nome__icontains', 'cpf__icontains'],
            attrs={
                'data-placeholder': 'Digite para buscar um sócio...',
                'data-width': '100%'  # <-- A MESMA CORREÇÃO APLICADA AQUI
            }
        )
    )
    
    class Meta:
        model = Conta
        fields = ['descricao', 'plano_de_contas', 'valor', 'data_vencimento', 'status', 'socio']
        widgets = {
            'data_vencimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        if empresa:
            # A view ainda controla o queryset inicial para segurança
            self.fields['plano_de_contas'].queryset = PlanoDeContas.objects.filter(empresa=empresa)
            self.fields['socio'].queryset = Socio.objects.filter(empresa=empresa)
        
        for field_name, field in self.fields.items():
            # Evita adicionar 'form-control' aos widgets do Select2
            if not isinstance(field.widget, ModelSelect2Widget):
                field.widget.attrs['class'] = 'form-control'


class BaixaContaForm(forms.Form):
    caixa = forms.ModelChoiceField(queryset=Caixa.objects.all(), label="Confirmar no Caixa / Conta")
    data_pagamento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data do Pagamento")

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['caixa'].queryset = Caixa.objects.filter(empresa=empresa)


class LancamentoCaixaForm(forms.ModelForm):
    class Meta:
        model = LancamentoCaixa
        fields = ['caixa', 'plano_de_contas', 'data_lancamento', 'descricao', 'valor']
        widgets = {
            'data_lancamento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'descricao': forms.TextInput(attrs={'placeholder': 'Ex: Pagamento conta de luz, Venda avulsa'}),
            'valor': forms.NumberInput(attrs={'placeholder': 'Use negativo para saídas. Ex: -50.00'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields['caixa'].queryset = Caixa.objects.filter(empresa=empresa)
            self.fields['plano_de_contas'].queryset = PlanoDeContas.objects.filter(empresa=empresa)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    
class LancamentoCaixaForm(forms.ModelForm):
    # 1. Novos campos que o usuário irá ver
    TIPO_CHOICES = [('C', 'Crédito (Entrada)'), ('D', 'Débito (Saída)')]
    tipo_lancamento = forms.ChoiceField(choices=TIPO_CHOICES, label="Tipo de Lançamento")
    valor_display = forms.DecimalField(max_digits=15, decimal_places=2, label="Valor (R$)")

    class Meta:
        model = LancamentoCaixa
        # O campo 'valor' do modelo é omitido do formulário direto, pois vamos calculá-lo
        fields = ['caixa', 'plano_de_contas', 'data_lancamento', 'descricao']
        widgets = {
            'data_lancamento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'descricao': forms.TextInput(attrs={'placeholder': 'Ex: Pagamento conta de luz, Venda avulsa'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        # Lógica para EDIÇÃO: pré-preenche os campos com base no valor já salvo no banco
        if self.instance and self.instance.pk:
            if self.instance.valor < 0:
                self.fields['tipo_lancamento'].initial = 'D'
                self.fields['valor_display'].initial = abs(self.instance.valor)
            else:
                self.fields['tipo_lancamento'].initial = 'C'
                self.fields['valor_display'].initial = self.instance.valor

        if empresa:
            self.fields['caixa'].queryset = Caixa.objects.filter(empresa=empresa)
            self.fields['plano_de_contas'].required = False
            self.fields['plano_de_contas'].empty_label = "Nenhum (usar para ajustes de caixa)"

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Adiciona a classe 'form-control' a todos os campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        """
        Método de validação que converte os campos de display para o campo 'valor' do modelo.
        """
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo_lancamento")
        valor = cleaned_data.get("valor_display")

        if tipo == 'D':
            # Se for Débito, tornamos o valor negativo para salvar no banco
            cleaned_data['valor'] = -abs(valor)
        else:
            # Se for Crédito, o valor já é positivo
            cleaned_data['valor'] = valor
        
        return cleaned_data

    def save(self, commit=True):
        """
        Sobrescreve o método save para garantir que nosso valor calculado seja usado.
        """
        # Pega o valor calculado do método clean()
        self.instance.valor = self.cleaned_data['valor']
        return super().save(commit)

class BaixaMensalidadeForm(forms.Form):
    caixa = forms.ModelChoiceField(queryset=Caixa.objects.all(), label="Confirmar no Caixa / Conta")
    data_pagamento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data do Pagamento")
    # Campo para juros, que será calculado automaticamente mas pode ser editado pelo admin
    valor_juros = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Juros / Multa (R$)")

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['caixa'].queryset = Caixa.objects.filter(empresa=empresa)        