# usuarios/urls.py

from django.urls import path
from .views import SiteLoginView, site_logout_view

# app_name define o "bairro" que usamos na tag {% url %}
app_name = 'usuarios'

urlpatterns = [
    # A rota para a nossa página de login, com o nome 'site-login'
    path('login/', SiteLoginView.as_view(), name='site-login'),
    
    # A rota para a nossa função de logout, com o nome 'site-logout'
    path('logout/', site_logout_view, name='site-logout'),
]