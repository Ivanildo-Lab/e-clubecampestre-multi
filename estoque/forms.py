from django import forms
from .models import Produto, CategoriaProduto, MovimentacaoEstoque
from fornecedores.models import Fornecedor


class CategoriaProdutoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProduto
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Bebidas, Alimentos, Material de Limpeza...'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descricao opcional da categoria...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 'descricao', 'codigo_barras', 'categoria', 'unidade',
            'preco_custo', 'preco_venda', 'estoque_atual', 'estoque_minimo', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do produto'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'codigo_barras': forms.TextInput(attrs={'placeholder': 'Codigo de barras (opcional)'}),
            'preco_custo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'preco_venda': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'estoque_atual': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'estoque_minimo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['categoria'].queryset = CategoriaProduto.objects.filter(empresa=empresa)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

    def clean_codigo_barras(self):
        codigo = self.cleaned_data.get('codigo_barras')
        if codigo:
            codigo = codigo.strip()
        return codigo if codigo else None


class MovimentacaoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = ['produto', 'tipo', 'quantidade', 'fornecedor', 'valor_compra', 'motivo', 'observacao']
        widgets = {
            'motivo': forms.TextInput(attrs={'placeholder': 'Ex: Compra, Venda, Ajuste de inventario...'}),
            'observacao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observacao opcional...'}),
            'quantidade': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'valor_compra': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['produto'].queryset = Produto.objects.filter(empresa=empresa, ativo=True)
            self.fields['fornecedor'].queryset = Fornecedor.objects.filter(empresa=empresa)
        self.fields['fornecedor'].required = False
        self.fields['valor_compra'].required = False
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        quantidade = cleaned_data.get('quantidade')
        produto = cleaned_data.get('produto')
        valor_compra = cleaned_data.get('valor_compra')

        if tipo and quantidade and produto:
            if tipo == 'SAIDA' and quantidade > produto.estoque_atual:
                raise forms.ValidationError(
                    f'Estoque insuficiente. Disponivel: {produto.estoque_atual} {produto.get_unidade_display()}'
                )
            if tipo == 'AJUSTE' and quantidade < 0:
                raise forms.ValidationError('Para ajuste, use a quantidade atual do estoque no campo quantidade.')
            if tipo == 'ENTRADA' and (not valor_compra or valor_compra <= 0):
                raise forms.ValidationError('Para entradas, o valor total da compra e obrigatorio.')
        return cleaned_data
