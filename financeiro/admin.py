from django.contrib import admin
from .models import (
    PlanoMensalidade, Mensalidade, CategoriaReceita, Receita,
    CategoriaDespesa, Despesa
)


@admin.register(PlanoMensalidade)
class PlanoMensalidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)


@admin.register(Mensalidade)
class MensalidadeAdmin(admin.ModelAdmin):
    list_display = ('socio', 'plano', 'referencia', 'valor', 'data_vencimento', 'status', 'data_pagamento')
    list_filter = ('status', 'forma_pagamento', 'data_vencimento', 'data_pagamento')
    search_fields = ('socio__nome_completo', 'referencia')
    ordering = ('-data_vencimento',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao', 'valor_pago')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('socio', 'plano', 'referencia', 'valor', 'data_vencimento')
        }),
        ('Pagamento', {
            'fields': ('status', 'data_pagamento', 'forma_pagamento', 'valor_pago')
        }),
        ('Valores Adicionais', {
            'fields': ('desconto', 'juros')
        }),
        ('Outros', {
            'fields': ('comprovante', 'observacoes', 'gerado_por', 'pago_por')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CategoriaReceita)
class CategoriaReceitaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data_prevista', 'status', 'data_recebimento')
    list_filter = ('status', 'categoria', 'data_prevista', 'data_recebimento')
    search_fields = ('descricao', 'categoria__nome')
    ordering = ('-data_prevista',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')


@admin.register(CategoriaDespesa)
class CategoriaDespesaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data_vencimento', 'status', 'data_pagamento')
    list_filter = ('status', 'categoria', 'data_vencimento', 'data_pagamento')
    search_fields = ('descricao', 'categoria__nome')
    ordering = ('-data_vencimento',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')