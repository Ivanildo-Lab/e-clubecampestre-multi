from django.contrib import admin
from .models import ConfiguracaoSistema, Auditoria, Backup, Notificacao


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor', 'ativo', 'data_criacao')
    list_filter = ('chave', 'ativo', 'data_criacao')
    search_fields = ('chave', 'descricao')
    ordering = ('chave',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao')


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'acao', 'modelo', 'data_acao', 'ip_address')
    list_filter = ('acao', 'modelo', 'data_acao')
    search_fields = ('usuario__username', 'descricao', 'objeto_id')
    ordering = ('-data_acao',)
    readonly_fields = ('id', 'data_acao', 'dados_antigos', 'dados_novos')


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'status', 'data_inicio', 'data_fim', 'tamanho_formatado')
    list_filter = ('tipo', 'status', 'data_inicio')
    search_fields = ('nome', 'descricao')
    ordering = ('-data_inicio',)
    readonly_fields = ('id', 'data_inicio', 'data_fim', 'tamanho')


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'prioridade', 'status', 'data_criacao')
    list_filter = ('tipo', 'prioridade', 'status', 'data_criacao')
    search_fields = ('titulo', 'mensagem', 'usuario__username')
    ordering = ('-data_criacao')
    readonly_fields = ('id', 'data_criacao', 'data_leitura', 'data_arquivamento')