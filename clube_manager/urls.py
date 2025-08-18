# clube_manager/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importe a nossa view da página inicial
from core.views import HomeView

urlpatterns = [
    # Rota para o Painel de Administração (Funcional)
    path('admin/', admin.site.urls),

    # Rota para a Página Inicial (Funcional)
    path('', HomeView.as_view(), name='home'),
    
    # --- ROTAS DA API ---
    # Vamos manter comentadas todas as rotas de apps cujas views
    # ainda não foram construídas. Nós vamos descomentar uma por uma
    # conforme formos desenvolvendo cada funcionalidade.

    # path('api/core/', include('core.urls')),
    # path('api/usuarios/', include('usuarios.urls')),
    path('socios/', include('socios.urls')),
    # path('api/financeiro/', include('financeiro.urls')),
    # path('api/cobranca/', include('cobranca.urls')),
    # path('api/eventos/', include('eventos.urls')),
    
]

# Configuração para servir arquivos estáticos e de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)