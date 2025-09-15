# financeiro/admin.py

from django.contrib import admin
from .models import Mensalidade, CategoriaTransacao, Transacao

class MensalidadeAdmin(admin.ModelAdmin):
    list_display = ('socio', 'competencia', 'valor', 'data_vencimento', 'status', 'data_pagamento')
    list_filter = ('status', 'competencia')
    search_fields = ('socio__nome', 'socio__cpf')
    list_editable = ('status', 'data_pagamento')
    autocomplete_fields = ['socio']

class CategoriaTransacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nome',)

class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data_transacao', 'socio')
    list_filter = ('categoria', 'data_transacao')
    search_fields = ('descricao', 'socio__nome')
    autocomplete_fields = ['socio', 'categoria']

admin.site.register(Mensalidade, MensalidadeAdmin)
admin.site.register(CategoriaTransacao, CategoriaTransacaoAdmin)
admin.site.register(Transacao, TransacaoAdmin)