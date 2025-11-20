# relatorios/forms.py

from django import forms
import datetime
from django.utils.formats import date_format
from financeiro.models import Conta
class FiltroInadimplenciaMensalForm(forms.Form):
    MESES_CHOICES = [(i, date_format(datetime.date(2000, i, 1), "F").capitalize()) for i in range(1, 13)]
    ANO_ATUAL = datetime.date.today().year
    ANOS_CHOICES = [(i, i) for i in range(ANO_ATUAL, ANO_ATUAL - 6, -1)]

    mes = forms.ChoiceField(choices=MESES_CHOICES, label="Mês de Competência", widget=forms.Select(attrs={'class': 'form-control'}))
    ano = forms.ChoiceField(choices=ANOS_CHOICES, label="Ano", widget=forms.Select(attrs={'class': 'form-control'}))

class FiltroContasForm(forms.Form):
    TIPO_CHOICES = [('', 'Todas'), ('RECEITA', 'A Receber'), ('DESPESA', 'A Pagar')]
    STATUS_CHOICES = [('', 'Todos os Status')] + Conta.StatusChoice.choices

    data_inicio = forms.DateField(label="Vencimento De", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    data_fim = forms.DateField(label="Até", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, required=False, label="Tipo", widget=forms.Select(attrs={'class': 'form-control'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label="Status")