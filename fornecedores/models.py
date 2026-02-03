from django.db import models
from core.models import Empresa

class Fornecedor(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255, verbose_name="Razão Social / Nome")
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Fantasia")
    cpf_cnpj = models.CharField(max_length=20, verbose_name="CPF/CNPJ", blank=True, null=True)
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    responsavel = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pessoa de Contato")
    
    # Endereço
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    
    observacoes = models.TextField(blank=True, null=True)
    data_cadastro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome_fantasia if self.nome_fantasia else self.nome

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']
        # Evita duplicidade de documento dentro da mesma empresa
        unique_together = ('empresa', 'cpf_cnpj')
        