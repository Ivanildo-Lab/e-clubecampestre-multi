from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    NIVEL_PERMISSAO_CHOICES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('FINANCEIRO', 'Financeiro'),
        ('ATENDIMENTO', 'Atendimento'),
    ]
    
    nivel_permissao = models.CharField(
        max_length=20,
        choices=NIVEL_PERMISSAO_CHOICES,
        default='ATENDIMENTO',
        verbose_name='Nível de Permissão'
    )
    
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefone'
    )
    
    foto = models.ImageField(
        upload_to='usuarios/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto'
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return self.nome or self.username
    
    @property
    def nome(self):
        return self.first_name + ' ' + self.last_name if self.first_name and self.last_name else self.username
    
    def has_permission(self, required_permission):
        """Verifica se o usuário tem a permissão necessária"""
        permission_hierarchy = {
            'ADMINISTRADOR': ['ADMINISTRADOR', 'FINANCEIRO', 'ATENDIMENTO'],
            'FINANCEIRO': ['FINANCEIRO', 'ATENDIMENTO'],
            'ATENDIMENTO': ['ATENDIMENTO']
        }
        
        return required_permission in permission_hierarchy.get(self.nivel_permissao, [])