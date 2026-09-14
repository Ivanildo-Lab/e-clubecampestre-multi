# financeiro/forms.py

import datetime

from django import forms
from django_select2.forms import ModelSelect2Widget
from .models import Conta, PlanoDeContas, Socio, Caixa, LancamentoCaixa,Mensalidade
from core.models import Convenio, CategoriaSocio
from fornecedores.models import Fornecedor

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


    def _get_next_codigo(self, empresa, parent):
        """Gera próximo código sequencial baseado no pai. Ex: pai 10.000.000 -> filhos 10.000.001, 10.000.002"""
        from django.db.models import Max
        if parent:
            # Busca maior código entre filhos do mesmo pai
            max_codigo = PlanoDeContas.objects.filter(empresa=empresa, parent=parent).aggregate(Max('codigo'))['codigo__max']
            if max_codigo:
                try:
                    # Tenta interpretar como número com pontos: 10.000.001 -> 10000001
                    base = parent.codigo.replace('.', '')
                    # Se filho tem código, incrementa último segmento
                    # Simples: pega max e incrementa
                    # Converte removendo pontos e incrementa
                    num = int(max_codigo.replace('.', ''))
                    nxt = num + 1
                    # Formata de volta com pontos a cada 3? Mantém formato do pai + 3 dígitos
                    # Ex: 10.000.000 -> 10.000.001
                    # Usa formato do pai para determinar casas
                    if '.' in parent.codigo:
                        # Mantém mesma quantidade de dígitos após último ponto
                        prefix = parent.codigo.rsplit('.', 1)[0]
                        last_len = len(parent.codigo.rsplit('.', 1)[1])
                        suffix = str(nxt).zfill(len(max_codigo.replace('.', '')))[-last_len:]
                        # Se não conseguiu, apenas incrementa
                        try:
                            suffix_num = int(max_codigo.split('.')[-1]) + 1
                            return f"{prefix}.{str(suffix_num).zfill(last_len)}"
                        except:
                            return str(nxt)
                    return str(nxt)
                except:
                    pass
            # Sem filhos: primeiro filho é pai + .001 ou .01
            if '.' in parent.codigo:
                return f"{parent.codigo.rsplit('.', 1)[0]}.{parent.codigo.split('.')[-1][:1]}001".replace('..', '.') if False else f"{parent.codigo}.001"
            return f"{parent.codigo}.001"
        else:
            # Sem pai: próximo código de nível raiz
            max_codigo = PlanoDeContas.objects.filter(empresa=empresa, parent__isnull=True).aggregate(Max('codigo'))['codigo__max']
            if max_codigo:
                try:
                    # Incrementa último número
                    parts = max_codigo.split('.')
                    last = int(parts[-1]) + 1
                    parts[-1] = str(last).zfill(len(parts[-1]))
                    return '.'.join(parts)
                except:
                    return str(int(max_codigo.replace('.', '')) + 1)
            return "10.000.000"

class PlanoDeContasForm(forms.ModelForm):
    class Meta:
        model = PlanoDeContas
        fields = ['codigo', 'nome', 'tipo', 'parent', 'aceita_lancamentos']
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Gerado automaticamente após escolher o pai'}),
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Receita de Mensalidades'}),
        }

    def __init__(self, *args, **kwargs):
        # Pega a empresa que a view vai nos passar
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields['parent'].queryset = PlanoDeContas.objects.filter(
                empresa=empresa,
                aceita_lancamentos=False
            )
            self.fields['parent'].empty_label = "Nenhuma (Conta Principal)"
            # Se for criação e já tem parent inicial, sugere próximo código
            if not self.instance.pk:
                parent_initial = None
                # Tenta pegar do initial ou do POST
                parent_id = self.initial.get('parent') or self.data.get('parent')
                if parent_id:
                    try:
                        parent_initial = PlanoDeContas.objects.get(id=parent_id, empresa=empresa)
                    except:
                        pass
                if parent_initial:
                    self.fields['codigo'].initial = self._get_next_codigo(empresa, parent_initial)
                elif not self.data.get('codigo'):
                    # Sugere próximo raiz se não tem pai
                    self.fields['codigo'].initial = self._get_next_codigo(empresa, None)
                    self.fields['codigo'].help_text = "Gerado automaticamente. Altere se necessário."

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
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.all(),
        label="Fornecedor (Opcional)",
        required=False,
        widget=ModelSelect2Widget(
            model=Fornecedor,
            search_fields=['nome__icontains', 'nome_fantasia__icontains'],
            attrs={'data-placeholder': 'Buscar Fornecedor...', 'data-width': '100%'}
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
        fields = ['descricao', 'plano_de_contas', 'fornecedor', 'valor', 'data_vencimento', 'status', 'socio'] 
        widgets = {
        'data_vencimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        tipo_filtro = kwargs.pop('tipo_filtro', None)
        super().__init__(*args, **kwargs)

        if empresa:
            qs = PlanoDeContas.objects.filter(empresa=empresa)
            if tipo_filtro == 'RECEITA':
                qs = qs.filter(tipo='RECEITA')
            elif tipo_filtro == 'DESPESA':
                qs = qs.filter(tipo='DESPESA')
            self.fields['plano_de_contas'].queryset = qs
            self.fields['socio'].queryset = Socio.objects.filter(empresa=empresa)
            self.fields['fornecedor'].queryset = Fornecedor.objects.filter(empresa=empresa)            
        
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

# Em financeiro/forms.py

class BaixaMensalidadeForm(forms.Form):
    caixa = forms.ModelChoiceField(
        queryset=Caixa.objects.all(),
        label="Confirmar no Caixa / Conta",
        required=False,
        empty_label="-- Nao lancar no caixa (Apenas baixar) --"
    )
    forma_pagamento = forms.ModelChoiceField(
        queryset=None,
        label="Forma de Pagamento",
        required=False,
        empty_label="-- Selecione --"
    )
    data_pagamento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data do Pagamento")
    valor_juros = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Juros / Multa (R$)")

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if empresa:
            from formas_pagamento.models import FormaPagamento
            self.fields['caixa'].queryset = Caixa.objects.filter(empresa=empresa)
            self.fields['forma_pagamento'].queryset = FormaPagamento.objects.filter(empresa=empresa, ativo=True)



class GerarMensalidadesForm(forms.Form):
    ORIGEM_CHOICES = [
        ('categoria', 'Por Categoria'),
        ('convenio', 'Por Convênio'),
    ]
    PERIODO_CHOICES = [
        ('mes', 'Apenas para o Mês Selecionado'),
        ('ano', '12 Meses a partir do Mês Selecionado'),
    ]

    origem = forms.ChoiceField(
        choices=ORIGEM_CHOICES,
        label="Gerar por",
        widget=forms.RadioSelect,
        initial='convenio'
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaSocio.objects.all(),
        label="Categoria",
        required=False,
        empty_label="Todas as Categorias"
    )
    convenio = forms.ModelChoiceField(
        queryset=Convenio.objects.all(),
        label="Convênio",
        required=False,
        empty_label="Todos os Convênios"
    )
    mes_referencia = forms.ChoiceField(label="Mês", required=False)
    ano_referencia = forms.ChoiceField(label="Ano", required=False)
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        label="Período de Geração",
        widget=forms.RadioSelect,
        initial='mes'
    )

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        import datetime
        from django.utils.formats import date_format
        hoje = datetime.date.today()
        # Meses - anos com intervalo maior para retroativo (10 anos atrás até 2 à frente)
        meses = [(str(i), date_format(datetime.date(2000, i, 1), "F").capitalize()) for i in range(1, 13)]
        anos = [(str(i), str(i)) for i in range(hoje.year - 10, hoje.year + 3)]
        self.fields['mes_referencia'].choices = meses
        self.fields['ano_referencia'].choices = anos
        # Default atual
        if not self.data.get('mes_referencia') and not self.initial.get('mes_referencia'):
            self.fields['mes_referencia'].initial = str(hoje.month)
            self.fields['ano_referencia'].initial = str(hoje.year)
        else:
            # Se já veio via POST/initial, mantém
            pass
        if empresa:
            self.fields['categoria'].queryset = CategoriaSocio.objects.filter(empresa=empresa)
            self.fields['convenio'].queryset = Convenio.objects.filter(empresa=empresa)
        self.fields['mes_referencia'].widget.attrs.update({'class': 'form-control'})
        self.fields['ano_referencia'].widget.attrs.update({'class': 'form-control'})
        self.fields['categoria'].widget.attrs.update({'class': 'form-control'})
        self.fields['convenio'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned = super().clean()
        origem = cleaned.get('origem')
        categoria = cleaned.get('categoria')
        convenio = cleaned.get('convenio')
        if origem == 'convenio' and not convenio:
            self.add_error('convenio', 'Preencha o campo convênio.')
        if origem == 'categoria' and not categoria:
            self.add_error('categoria', 'Preencha o campo categoria.')
        # Valida mes/ano - apenas se ambos preenchidos, senão usa padrão
        mes = cleaned.get('mes_referencia')
        ano = cleaned.get('ano_referencia')
        if mes and ano:
            try:
                datetime.date(int(ano), int(mes), 1)
            except Exception as e:
                import logging
                logging.getLogger('clube_manager').error(f"Falha mes/ano: mes={mes!r} ano={ano!r} erro={e}")
                self.add_error('mes_referencia', 'Mês/ano inválido.')                
        return cleaned


class GerarMensalidadePorSocioForm(forms.Form):
    socio = forms.ModelChoiceField(
        queryset=Socio.objects.all(),
        label="Sócio",
        widget=ModelSelect2Widget(
            model=Socio,
            search_fields=['nome__icontains', 'cpf__icontains', 'num_registro__icontains'],
            attrs={'data-placeholder': 'Digite nome, CPF ou registro...', 'data-width': '100%'}
        )
    )
    periodo = forms.ChoiceField(
        choices=[('mes', 'Apenas Mês Atual'), ('ano', 'Próximos 12 Meses')],
        label="Período",
        widget=forms.RadioSelect,
        initial='mes'
    )
    data_vencimento_primeira = forms.DateField(
        label="Venc. da Primeira",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        help_text="Deixe em branco para usar hoje. Permite retroativo."
    )
    quantidade_parcelas = forms.IntegerField(
        label="Quantidade de Parcelas",
        min_value=1, max_value=24, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '24'}),
        help_text="1 para apenas um mês, até 24"
    )
    valor = forms.DecimalField(
        label="Valor (R$)",
        max_digits=10, decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Deixe vazio para usar do convênio/categoria'}),
        help_text="Deixe vazio para usar valor do convênio/categoria"
    )

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['socio'].queryset = Socio.objects.filter(empresa=empresa, situacao='ATIVO').order_by('nome')
        self.fields['data_vencimento_primeira'].widget.attrs['class'] = 'form-control'
        # Select2 já cuida do estilo, periodo é radio
