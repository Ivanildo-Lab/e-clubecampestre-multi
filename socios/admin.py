from django.contrib import admin
from .models import Socio, Dependente, InteracaoSocio


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', 'telefone', 'ativo', 'data_cadastro')
    list_filter = ('ativo', 'estado_civil', 'data_cadastro')
    search_fields = ('nome_completo', 'email', 'cpf', 'telefone')
    ordering = ('-data_cadastro',)
    readonly_fields = ('id', 'data_cadastro', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_completo', 'cpf', 'rg', 'data_nascimento', 'estado_civil', 'tipo_sanguineo')
        }),
        ('Contato', {
            'fields': ('email', 'telefone', 'telefone_secundario')
        }),
        ('Endereço', {
            'fields': ('endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Profissionais', {
            'fields': ('profissao', 'empresa')
        }),
        ('Outros', {
            'fields': ('foto', 'observacoes', 'ativo', 'cadastrado_por')
        }),
        ('Datas', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Dependente)
class DependenteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'socio', 'parentesco', 'ativo', 'data_cadastro')
    list_filter = ('parentesco', 'ativo', 'data_cadastro')
    search_fields = ('nome_completo', 'socio__nome_completo')
    ordering = ('nome_completo',)
    readonly_fields = ('id', 'data_cadastro', 'data_atualizacao')


@admin.register(InteracaoSocio)
class InteracaoSocioAdmin(admin.ModelAdmin):
    list_display = ('socio', 'tipo', 'data_interacao', 'usuario')
    list_filter = ('tipo', 'data_interacao')
    search_fields = ('socio__nome_completo', 'descricao')
    ordering = ('-data_interacao',)
    readonly_fields = ('id', )