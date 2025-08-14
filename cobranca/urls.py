from django.urls import path
from . import views

app_name = 'cobranca'

urlpatterns = [
    path('templates/', views.TemplateCobrancaListView.as_view(), name='template-list'),
    path('templates/create/', views.TemplateCobrancaCreateView.as_view(), name='template-create'),
    path('templates/<uuid:pk>/', views.TemplateCobrancaDetailView.as_view(), name='template-detail'),
    
    path('campanhas/', views.CampanhaCobrancaListView.as_view(), name='campanha-list'),
    path('campanhas/create/', views.CampanhaCobrancaCreateView.as_view(), name='campanha-create'),
    path('campanhas/<uuid:pk>/', views.CampanhaCobrancaDetailView.as_view(), name='campanha-detail'),
    path('campanhas/<uuid:pk>/executar/', views.CampanhaCobrancaExecutarView.as_view(), name='campanha-executar'),
    
    path('envios/', views.EnvioCobrancaListView.as_view(), name='envio-list'),
    path('envios/<uuid:pk>/', views.EnvioCobrancaDetailView.as_view(), name='envio-detail'),
    
    path('historico/', views.HistoricoCobrancaListView.as_view(), name='historico-list'),
]