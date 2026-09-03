from django.urls import path
from .views import (
    ProdutoListView, ProdutoCreateView, ProdutoUpdateView, ProdutoDeleteView,
    MovimentacaoEstoqueListView, MovimentacaoEstoqueCreateView,
    CategoriaProdutoListView, CategoriaProdutoCreateView,
    CategoriaProdutoUpdateView, CategoriaProdutoDeleteView,
    EstoquePDFView, MovimentacaoEstoquePDFView,
)

app_name = 'estoque'

urlpatterns = [
    path('', ProdutoListView.as_view(), name='lista_produtos'),
    path('adicionar/', ProdutoCreateView.as_view(), name='adicionar_produto'),
    path('<int:pk>/editar/', ProdutoUpdateView.as_view(), name='editar_produto'),
    path('<int:pk>/excluir/', ProdutoDeleteView.as_view(), name='excluir_produto'),
    path('movimentacoes/', MovimentacaoEstoqueListView.as_view(), name='lista_movimentacoes'),
    path('movimentacoes/adicionar/', MovimentacaoEstoqueCreateView.as_view(), name='adicionar_movimentacao'),
    path('categorias/', CategoriaProdutoListView.as_view(), name='lista_categorias'),
    path('categorias/adicionar/', CategoriaProdutoCreateView.as_view(), name='adicionar_categoria'),
    path('categorias/<int:pk>/editar/', CategoriaProdutoUpdateView.as_view(), name='editar_categoria'),
    path('categorias/<int:pk>/excluir/', CategoriaProdutoDeleteView.as_view(), name='excluir_categoria'),
    path('pdf/', EstoquePDFView.as_view(), name='estoque_pdf'),
    path('movimentacoes/pdf/', MovimentacaoEstoquePDFView.as_view(), name='movimentacoes_pdf'),
]
