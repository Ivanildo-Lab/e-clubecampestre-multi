from django.urls import path
from . import views

app_name = 'socios'

urlpatterns = [
    path('', views.SocioListView.as_view(), name='socio-list'),
    path('create/', views.SocioCreateView.as_view(), name='socio-create'),
    path('<uuid:pk>/', views.SocioDetailView.as_view(), name='socio-detail'),
    path('<uuid:pk>/update/', views.SocioUpdateView.as_view(), name='socio-update'),
    path('<uuid:pk>/delete/', views.SocioDeleteView.as_view(), name='socio-delete'),
    path('<uuid:pk>/dependentes/', views.DependenteListView.as_view(), name='dependente-list'),
    path('<uuid:pk>/dependentes/create/', views.DependenteCreateView.as_view(), name='dependente-create'),
    path('<uuid:socio_pk>/dependentes/<uuid:pk>/', views.DependenteDetailView.as_view(), name='dependente-detail'),
    path('<uuid:socio_pk>/dependentes/<uuid:pk>/update/', views.DependenteUpdateView.as_view(), name='dependente-update'),
    path('<uuid:socio_pk>/dependentes/<uuid:pk>/delete/', views.DependenteDeleteView.as_view(), name='dependente-delete'),
    path('<uuid:pk>/interacoes/', views.InteracaoSocioListView.as_view(), name='interacao-list'),
    path('<uuid:pk>/interacoes/create/', views.InteracaoSocioCreateView.as_view(), name='interacao-create'),
]