from django.contrib import admin
from .models import FormaPagamento


@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'empresa')
    search_fields = ('nome',)
