from django.contrib import admin
from .models import TemplateCobranca, CampanhaCobranca, EnvioCobranca, HistoricoCobranca


@admin.register(TemplateCobranca)
class TemplateCobrancaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'ativo', 'data_criacao')
    list_filter = ('tipo', 'ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')


@admin.register(CampanhaCobranca)
class CampanhaCobrancaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'template', 'status', 'data_inicio', 'total_envios', 'total_sucesso')
    list_filter = ('status', 'template', 'data_inicio', 'data_fim')
    search_fields = ('nome', 'descricao')
    ordering = ('-data_criacao',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'template', 'status')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Destinatários', {
            'fields': ('destinatarios', 'filtro_status_mensalidade', 'filtro_dias_atraso')
        }),
        ('Estatísticas', {
            'fields': ('total_envios', 'total_sucesso', 'total_falhas'),
            'classes': ('collapse',)
        }),
        ('Outros', {
            'fields': ('criado_por',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EnvioCobranca)
class EnvioCobrancaAdmin(admin.ModelAdmin):
    list_display = ('campanha', 'socio', 'mensalidade', 'status', 'data_envio')
    list_filter = ('status', 'campanha', 'data_envio')
    search_fields = ('socio__nome_completo', 'campanha__nome')
    ordering = ('-data_criacao',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')


@admin.register(HistoricoCobranca)
class HistoricoCobrancaAdmin(admin.ModelAdmin):
    list_display = ('socio', 'mensalidade', 'acao', 'data_acao', 'usuario')
    list_filter = ('acao', 'data_acao')
    search_fields = ('socio__nome_completo', 'descricao')
    ordering = ('-data_acao',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')