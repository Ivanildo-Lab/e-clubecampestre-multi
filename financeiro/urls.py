from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    path('planos/', views.PlanoMensalidadeListView.as_view(), name='plano-list'),
    path('planos/create/', views.PlanoMensalidadeCreateView.as_view(), name='plano-create'),
    path('planos/<uuid:pk>/', views.PlanoMensalidadeDetailView.as_view(), name='plano-detail'),
    path('planos/<uuid:pk>/update/', views.PlanoMensalidadeUpdateView.as_view(), name='plano-update'),
    
    path('mensalidades/', views.MensalidadeListView.as_view(), name='mensalidade-list'),
    path('mensalidades/create/', views.MensalidadeCreateView.as_view(), name='mensalidade-create'),
    path('mensalidades/<uuid:pk>/', views.MensalidadeDetailView.as_view(), name='mensalidade-detail'),
    path('mensalidades/<uuid:pk>/update/', views.MensalidadeUpdateView.as_view(), name='mensalidade-update'),
    path('mensalidades/<uuid:pk>/pagar/', views.MensalidadePagarView.as_view(), name='mensalidade-pagar'),
    path('mensalidades/gerar/', views.MensalidadeGerarView.as_view(), name='mensalidade-gerar'),
    
    path('receitas/', views.ReceitaListView.as_view(), name='receita-list'),
    path('receitas/create/', views.ReceitaCreateView.as_view(), name='receita-create'),
    path('receitas/<uuid:pk>/', views.ReceitaDetailView.as_view(), name='receita-detail'),
    
    path('despesas/', views.DespesaListView.as_view(), name='despesa-list'),
    path('despesas/create/', views.DespesaCreateView.as_view(), name='despesa-create'),
    path('despesas/<uuid:pk>/', views.DespesaDetailView.as_view(), name='despesa-detail'),
    
    path('relatorios/mensal/', views.RelatorioMensalView.as_view(), name='relatorio-mensal'),
    path('relatorios/anual/', views.RelatorioAnualView.as_view(), name='relatorio-anual'),
]