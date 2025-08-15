# core/context_processors.py

from .models import Empresa

def empresa_context(request):
    """
    Torna os dados da primeira empresa cadastrada disponíveis em todos os templates.
    """
    empresa_ativa = Empresa.objects.first()
    return {
        'empresa_ativa': empresa_ativa
    }