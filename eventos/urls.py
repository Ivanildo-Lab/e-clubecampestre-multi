from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    path('', views.EventoListView.as_view(), name='evento-list'),
    path('create/', views.EventoCreateView.as_view(), name='evento-create'),
    path('<uuid:pk>/', views.EventoDetailView.as_view(), name='evento-detail'),
    path('<uuid:pk>/update/', views.EventoUpdateView.as_view(), name='evento-update'),
    path('<uuid:pk>/delete/', views.EventoDeleteView.as_view(), name='evento-delete'),
    
    path('inscricoes/', views.InscricaoEventoListView.as_view(), name='inscricao-list'),
    path('inscricoes/create/', views.InscricaoEventoCreateView.as_view(), name='inscricao-create'),
    path('inscricoes/<uuid:pk>/', views.InscricaoEventoDetailView.as_view(), name='inscricao-detail'),
    path('inscricoes/<uuid:pk>/confirmar/', views.InscricaoEventoConfirmarView.as_view(), name='inscricao-confirmar'),
    path('inscricoes/<uuid:pk>/cancelar/', views.InscricaoEventoCancelarView.as_view(), name='inscricao-cancelar'),
    
    path('checkin/', views.CheckinEventoListView.as_view(), name='checkin-list'),
    path('checkin/create/', views.CheckinEventoCreateView.as_view(), name='checkin-create'),
]