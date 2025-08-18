from django.contrib import admin
# Vamos importar apenas os modelos que realmente existem agora
from .models import Socio, CategoriaSocio, Convenio, Empresa, Dependente

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
        ('Mídia e Outros', {'fields': ('logo', 'observacoes')}),
    )

# Registra os outros modelos que não precisam de configuração especial
admin.site.register(CategoriaSocio)
admin.site.register(Convenio)
