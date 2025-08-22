# socios/urls.py
from django.urls import path
from .views import SocioListView,SocioCreateView , SocioUpdateView,SocioDeleteView, GerarMensalidadeIndividualView 
from .views import (
    # ... views de socio
    CategoriaSocioListView, CategoriaSocioCreateView,
    CategoriaSocioUpdateView, CategoriaSocioDeleteActionView ,
    # ... views de convenio
    ConvenioListView, ConvenioCreateView,
    ConvenioUpdateView, ConvenioDeleteActionView

)

app_name = 'socios'

urlpatterns = [
    path('', SocioListView.as_view(), name='lista_socios'),
    path('adicionar/', SocioCreateView.as_view(), name='adicionar_socio'),
    path('<int:pk>/editar/', SocioUpdateView.as_view(), name='editar_socio'),
    path('<int:pk>/excluir/', SocioDeleteView.as_view(), name='excluir_socio'),
    path('<int:pk>/gerar-mensalidade/', GerarMensalidadeIndividualView.as_view(), name='gerar_mensalidade_individual'),
    path('categorias/', CategoriaSocioListView.as_view(), name='lista_categorias'),
    path('categorias/adicionar/', CategoriaSocioCreateView.as_view(), name='adicionar_categoria'),
    path('categorias/<int:pk>/editar/', CategoriaSocioUpdateView.as_view(), name='editar_categoria'),
    path('categorias/<int:pk>/delete-action/', CategoriaSocioDeleteActionView.as_view(), name='excluir_categoria_action'),
    path('convenios/', ConvenioListView.as_view(), name='lista_convenios'),
    path('convenios/adicionar/', ConvenioCreateView.as_view(), name='adicionar_convenio'),
    path('convenios/<int:pk>/editar/', ConvenioUpdateView.as_view(), name='editar_convenio'),
    path('convenios/<int:pk>/delete-action/', ConvenioDeleteActionView.as_view(), name='excluir_convenio_action'),
]