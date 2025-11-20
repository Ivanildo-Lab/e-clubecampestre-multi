# clube_manager/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from core.views import HomeView, LandingPageView, HelpView

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- ROTAS PRINCIPAIS DO SITE ---
    path('dashboard/', login_required(HomeView.as_view()), name='home'),
    path('', LandingPageView.as_view(), name='landing_page'),

    # --- ROTAS DOS APPS ---
    # ESTA LINHA CONECTA O MAPA MESTRE AO MAPA DO BAIRRO 'usuarios'
    path('usuarios/', include('usuarios.urls')),
    
    path('socios/', include('socios.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('select2/', include('django_select2.urls')),
    path('ajuda/', login_required(HelpView.as_view()), name='ajuda'),
]

# Configuração para servir arquivos de mídia e estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)