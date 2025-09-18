# core/admin.py

from django.contrib import admin
from .models import Socio, CategoriaSocio, Convenio, Empresa, Dependente, ConfiguracaoSistema

# --- Classes de Configuração do Admin ---

class DependenteInline(admin.TabularInline):
    """
    Permite editar os Dependentes na mesma página do Sócio.
    """
    model = Dependente
    extra = 1
    fields = ('nome', 'data_nascimento', 'parentesco', 'cpf', 'foto')

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'num_registro', 'cpf', 'categoria', 'situacao')
    search_fields = ('nome', 'cpf', 'num_registro')
    list_filter = ('situacao', 'categoria')
    inlines = [DependenteInline]

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'estado', 'responsavel', 'telefone')
    search_fields = ('nome', 'cidade')
    fieldsets = (
        ('Dados Gerais', {'fields': ('nome', 'responsavel')}),
        ('Endereço e Contato', {'fields': ('endereco', 'cidade', 'estado', 'telefone')}),
        ('Mídia e Outros', {'fields': ('logo', 'imagem_hero', 'observacoes')}),    )

@admin.register(CategoriaSocio)
class CategoriaSocioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_mensalidade', 'dia_vencimento')
    search_fields = ('nome',)
    
admin.site.register(Convenio)

@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor', 'empresa')
    list_filter = ('empresa',)
    search_fields = ('chave',)