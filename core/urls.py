from django.urls import path, re_path
from .views import ConfiguracaoListView, ConfiguracaoUpdateView, serve_media

urlpatterns = [
    path('configuracoes/', ConfiguracaoListView.as_view(), name='configuracoes_list'),
    path('configuracoes/<int:pk>/editar/', ConfiguracaoUpdateView.as_view(), name='editar_configuracao'),
    # Servir arquivos de mídia em produção (DEBUG=False)
    re_path(r'^media/(?P<path>.*)$', serve_media, name='serve_media'),
]