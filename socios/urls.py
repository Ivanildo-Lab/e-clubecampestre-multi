# socios/urls.py
from django.urls import path
from .views import SocioListView,SocioCreateView , SocioUpdateView,SocioDeleteView, GerarMensalidadeIndividualView 

app_name = 'socios'

urlpatterns = [
    path('', SocioListView.as_view(), name='lista_socios'),
    path('adicionar/', SocioCreateView.as_view(), name='adicionar_socio'),
    path('<int:pk>/editar/', SocioUpdateView.as_view(), name='editar_socio'),
    path('<int:pk>/excluir/', SocioDeleteView.as_view(), name='excluir_socio'),
    path('<int:pk>/gerar-mensalidade/', GerarMensalidadeIndividualView.as_view(), name='gerar_mensalidade_individual'),
]