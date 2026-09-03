from django.urls import path
from .views import VendaPDVView, VendaListView, VendaDetailView, VendaCancelarView, ProdutoAjaxSearchView

app_name = 'vendas'

urlpatterns = [
    path('', VendaListView.as_view(), name='historico'),
    path('nova/', VendaPDVView.as_view(), name='pdv'),
    path('api/produtos/', ProdutoAjaxSearchView.as_view(), name='api_produtos'),
    path('<int:pk>/', VendaDetailView.as_view(), name='detalhe'),
    path('<int:pk>/cancelar/', VendaCancelarView.as_view(), name='cancelar'),
]
