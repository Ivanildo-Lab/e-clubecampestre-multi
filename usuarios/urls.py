from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('register/', views.UsuarioCreateView.as_view(), name='usuario-create'),
    path('login/', views.UsuarioLoginView.as_view(), name='usuario-login'),
    path('logout/', views.UsuarioLogoutView.as_view(), name='usuario-logout'),
    path('profile/', views.UsuarioProfileView.as_view(), name='usuario-profile'),
    path('profile/update/', views.UsuarioProfileUpdateView.as_view(), name='usuario-profile-update'),
    path('list/', views.UsuarioListView.as_view(), name='usuario-list'),
    path('<uuid:pk>/', views.UsuarioDetailView.as_view(), name='usuario-detail'),
    path('permissions/', views.UsuarioPermissionsView.as_view(), name='usuario-permissions'),
]