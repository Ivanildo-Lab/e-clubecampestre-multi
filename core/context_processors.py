# Em core/context_processors.py
from .models import Empresa

def empresa_context(request):
    """
    Torna a empresa do usuário logado disponível em todos os templates.
    """
    empresa_ativa = None
    # Verifica se o usuário está autenticado e não é anônimo
    if request.user.is_authenticated:
        # Pega a empresa associada ao perfil do usuário
        empresa_ativa = request.user.empresa
    
    return {
        'empresa_ativa': empresa_ativa
    }