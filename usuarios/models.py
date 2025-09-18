from django.contrib.auth.models import AbstractUser
from django.db import models
# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import Empresa # Importamos nosso modelo de Empresa

# Em usuarios/models.py

class Usuario(AbstractUser):
    class NivelAcesso(models.TextChoices):
        OPERADOR = 'OPERADOR', 'Operador'
        ADMIN = 'ADMIN', 'Administrador'

    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.PROTECT,
        related_name='usuarios',
        null=True,
        blank=True
    )
    nivel_acesso = models.CharField(
        max_length=15,
        choices=NivelAcesso.choices,
        default=NivelAcesso.OPERADOR,
        verbose_name="Nível de Acesso"
    )
    # ...