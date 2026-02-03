from django.urls import path
from .views import (
    FornecedorListView, FornecedorCreateView,
    FornecedorUpdateView, FornecedorDeleteActionView
)

app_name = 'fornecedores'

urlpatterns = [
    path('', FornecedorListView.as_view(), name='lista_fornecedores'),
    path('adicionar/', FornecedorCreateView.as_view(), name='adicionar_fornecedor'),
    path('<int:pk>/editar/', FornecedorUpdateView.as_view(), name='editar_fornecedor'),
    path('<int:pk>/excluir/', FornecedorDeleteActionView.as_view(), name='excluir_fornecedor'),
]