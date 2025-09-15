from django.contrib.auth.models import AbstractUser
from django.db import models
# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import Empresa # Importamos nosso modelo de Empresa

class Usuario(AbstractUser):
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.PROTECT, # Impede que uma empresa com usuários seja apagada
        related_name='usuarios',
        null=True, # Permitir nulo temporariamente para o superuser inicial
        blank=True
    )

    def __str__(self):
        return self.username