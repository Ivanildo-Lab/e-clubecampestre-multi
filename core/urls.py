from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('configuracoes/', views.ConfiguracaoSistemaListView.as_view(), name='configuracao-list'),
    path('configuracoes/<uuid:pk>/', views.ConfiguracaoSistemaDetailView.as_view(), name='configuracao-detail'),
    path('auditoria/', views.AuditoriaListView.as_view(), name='auditoria-list'),
    path('notificacoes/', views.NotificacaoListView.as_view(), name='notificacao-list'),
    path('notificacoes/<uuid:pk>/marcar-lida/', views.NotificacaoMarcarLidaView.as_view(), name='notificacao-marcar-lida'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]