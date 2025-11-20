# relatorios/urls.py
from django.urls import path
from .views import (
    RelatorioInadimplenciaView, RelatorioInadimplenciaPDFView,
    RelatorioContasView, RelatorioDREView, RelatorioContasPDFView
)

app_name = 'relatorios'

urlpatterns = [
    path('inadimplencia/', RelatorioInadimplenciaView.as_view(), name='inadimplencia'),
    path('inadimplencia/pdf/', RelatorioInadimplenciaPDFView.as_view(), name='inadimplencia_pdf'),
    path('contas/', RelatorioContasView.as_view(), name='contas'),
    path('contas/pdf/', RelatorioContasPDFView.as_view(), name='contas_pdf'),
    path('dre/', RelatorioDREView.as_view(), name='dre'),
]