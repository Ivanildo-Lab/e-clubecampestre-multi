# financeiro/admin.py

from django.contrib import admin
# Importamos os NOVOS modelos que criamos
from .models import Mensalidade, Caixa, PlanoDeContas, Conta, LancamentoCaixa

@admin.register(Mensalidade)
class MensalidadeAdmin(admin.ModelAdmin):
    list_display = ('socio', 'competencia', 'valor', 'data_vencimento', 'status', 'data_pagamento')
    list_filter = ('status', 'competencia', 'socio__empresa')
    search_fields = ('socio__nome', 'socio__cpf')
    list_editable = ('status', 'data_pagamento')
    autocomplete_fields = ['socio']
    list_per_page = 20

@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'saldo_inicial')
    list_filter = ('empresa',)
    search_fields = ('nome',)

@admin.register(PlanoDeContas)
class PlanoDeContasAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'empresa')
    list_filter = ('tipo', 'empresa')
    search_fields = ('nome',)

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'plano_de_contas', 'valor', 'data_vencimento', 'status', 'empresa')
    list_filter = ('status', 'empresa', 'plano_de_contas')
    search_fields = ('descricao', 'socio__nome')
    autocomplete_fields = ['socio', 'plano_de_contas']
    list_per_page = 20

@admin.register(LancamentoCaixa)
class LancamentoCaixaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'caixa', 'plano_de_contas', 'data_lancamento', 'valor', 'empresa')
    list_filter = ('caixa', 'empresa', 'plano_de_contas', 'data_lancamento')
    search_fields = ('descricao',)
    list_per_page = 20
    # Torna o campo de valor somente leitura para evitar alterações acidentais
    readonly_fields = ('valor',)