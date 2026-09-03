from django.contrib import admin
from .models import Produto, CategoriaProduto, MovimentacaoEstoque


@admin.register(CategoriaProduto)
class CategoriaProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'data_criacao')
    list_filter = ('empresa',)
    search_fields = ('nome',)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'unidade', 'preco_custo', 'preco_venda', 'estoque_atual', 'estoque_minimo', 'ativo')
    list_filter = ('ativo', 'categoria', 'empresa')
    search_fields = ('nome', 'codigo_barras')
    list_editable = ('estoque_atual', 'ativo')


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'motivo', 'data_movimentacao', 'usuario')
    list_filter = ('tipo', 'data_movimentacao')
    search_fields = ('produto__nome', 'motivo')
    readonly_fields = ('data_movimentacao',)
