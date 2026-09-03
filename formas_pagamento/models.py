from django.db import models
from core.models import Empresa


class FormaPagamento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='formas_pagamento')
    nome = models.CharField(max_length=50, verbose_name="Nome")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Forma de Pagamento"
        verbose_name_plural = "Formas de Pagamento"
        unique_together = ('empresa', 'nome')
        ordering = ['nome']
