from django.contrib import admin
from .models import Evento, InscricaoEvento, ConvidadoEvento, CheckinEvento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'data_inicio', 'data_fim', 'local', 'status', 'inscricoes_abertas')
    list_filter = ('tipo', 'status', 'inscricoes_abertas', 'data_inicio')
    search_fields = ('nome', 'descricao', 'local')
    ordering = ('-data_inicio',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'tipo', 'status')
        }),
        ('Data e Local', {
            'fields': ('data_inicio', 'data_fim', 'local', 'endereco')
        }),
        ('Capacidade e Ingressos', {
            'fields': ('capacidade_maxima', 'valor_ingresso_socio', 'valor_ingresso_convidado')
        }),
        ('Convidados', {
            'fields': ('permite_convidados', 'max_convidados_por_socio')
        }),
        ('Controle', {
            'fields': ('inscricoes_abertas', 'requer_confirmacao', 'imagem')
        }),
        ('Organização', {
            'fields': ('organizador', 'observacoes')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InscricaoEvento)
class InscricaoEventoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'socio', 'quantidade_convidados', 'status', 'data_inscricao', 'valor_total')
    list_filter = ('status', 'evento', 'data_inscricao')
    search_fields = ('socio__nome_completo', 'evento__nome')
    ordering = ('-data_inscricao',)
    readonly_fields = ('id', 'data_inscricao', 'data_atualizacao', 'valor_total')


@admin.register(ConvidadoEvento)
class ConvidadoEventoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'inscricao', 'parentesco', 'compareceu')
    list_filter = ('compareceu', 'inscricao__evento')
    search_fields = ('nome_completo', 'inscricao__socio__nome_completo')
    ordering = ('nome_completo',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')


@admin.register(CheckinEvento)
class CheckinEventoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'socio', 'data_checkin', 'usuario_checkin')
    list_filter = ('evento', 'data_checkin')
    search_fields = ('socio__nome_completo', 'evento__nome')
    ordering = ('-data_checkin',)
    readonly_fields = ('id', 'data_checkin')