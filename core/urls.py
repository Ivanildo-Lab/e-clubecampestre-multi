from django.urls import path
from .views import ConfiguracaoListView, ConfiguracaoUpdateView

urlpatterns = [
    path('configuracoes/', ConfiguracaoListView.as_view(), name='configuracoes_list'),
    path('configuracoes/<int:pk>/editar/', ConfiguracaoUpdateView.as_view(), name='editar_configuracao'),
]