# core/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

# ==============================================================================
# MODELOS ATIVOS QUE ESTAMOS USANDO
# ==============================================================================

# Modelo para as Categorias dos Sócios
class CategoriaSocio(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Sócio"
        verbose_name_plural = "Categorias de Sócios"

# Modelo para os Convênios
class Convenio(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    empresa_contato = models.CharField(max_length=100, blank=True)
    telefone_contato = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nome

# Modelo Principal de Sócio
class Socio(models.Model):
    class EstadoCivil(models.TextChoices):
        SOLTEIRO = 'SOLTEIRO', 'Solteiro(a)'
        CASADO = 'CASADO', 'Casado(a)'
        DIVORCIADO = 'DIVORCIADO', 'Divorciado(a)'
        VIUVO = 'VIUVO', 'Viúvo(a)'
        UNIAO_ESTAVEL = 'UNIAO', 'União Estável'
    class Situacao(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        INATIVO = 'INATIVO', 'Inativo'
        SUSPENSO = 'SUSPENSO', 'Suspenso'
        CANCELADO = 'CANCELADO', 'Cancelado'

    num_registro = models.IntegerField(unique=True, help_text="Número de registro único do sócio.")
    num_contrato = models.IntegerField(unique=True, blank=True, null=True, help_text="Número do contrato, se aplicável.")
    categoria = models.ForeignKey(CategoriaSocio, on_delete=models.PROTECT, related_name='socios')
    convenio = models.ForeignKey(Convenio, on_delete=models.SET_NULL, blank=True, null=True, related_name='socios')
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    apelido = models.CharField(max_length=100, blank=True)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, blank=True, verbose_name="RG")
    nacionalidade = models.CharField(max_length=100, blank=True, default="Brasileira")
    naturalidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade Natal")
    estado_civil = models.CharField(max_length=10, choices=EstadoCivil.choices, blank=True)
    profissao = models.CharField(max_length=100, blank=True)
    nome_pai = models.CharField(max_length=255, blank=True, verbose_name="Nome do Pai")
    nome_mae = models.CharField(max_length=255, blank=True, verbose_name="Nome da Mãe")
    email = models.EmailField(unique=True, blank=True, null=True)
    tel_residencial = models.CharField(max_length=20, blank=True, verbose_name="Telefone Residencial")
    tel_trabalho = models.CharField(max_length=20, blank=True, verbose_name="Telefone do Trabalho")
    endereco = models.CharField(max_length=255, blank=True, verbose_name="Endereço (Rua, Nº)")
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True, verbose_name="UF")
    cep = models.CharField(max_length=9, blank=True, verbose_name="CEP")
    data_admissao = models.DateField(default=timezone.now)
    situacao = models.CharField(max_length=10, choices=Situacao.choices, default=Situacao.ATIVO)
    foto = models.ImageField(upload_to='fotos_socios/', blank=True, null=True)
    observacoes = models.TextField(blank=True, verbose_name="Observações")

    def __str__(self):
        return f"{self.nome} (Matrícula: {self.num_registro})"
    class Meta:
        verbose_name = "Sócio"
        verbose_name_plural = "Sócios"
        ordering = ['nome']

# Modelo de Dependente
class Dependente(models.Model):
    socio_titular = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='dependentes')
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, verbose_name="CPF")
    class TipoParentesco(models.TextChoices):
        CONJUGE = 'CONJUGE', 'Cônjuge'
        FILHO = 'FILHO', 'Filho(a)'
        PAI = 'PAI', 'Pai'
        MAE = 'MAE', 'Mãe'
        OUTRO = 'OUTRO', 'Outro'
    parentesco = models.CharField(
        max_length=10, 
        choices=TipoParentesco.choices, 
        verbose_name="Parentesco"
    )
    foto = models.ImageField(upload_to='fotos_dependentes/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.nome} (Dependente de {self.socio_titular.nome})"
    class Meta:
        verbose_name = "Dependente"
        verbose_name_plural = "Dependentes"
        ordering = ['nome']

# Modelo de Empresa
class Empresa(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    responsavel = models.CharField(max_length=150, blank=True, verbose_name="Responsável")
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    endereco = models.CharField(max_length=255, blank=True, verbose_name="Endereço (Rua, Nº, Bairro)")
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, verbose_name="UF")
    logo = models.ImageField(upload_to='logos_empresas/', blank=True, null=True, verbose_name="Logotipo")
    observacoes = models.TextField(blank=True, verbose_name="Observações")

    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"


# ==============================================================================
# MODELOS AVANÇADOS (DESATIVADOS TEMPORARIAMENTE)
# Vamos reativá-los no futuro, quando precisarmos deles.
# ==============================================================================
#
# Usuario = get_user_model()
#
# class ConfiguracaoSistema(models.Model):
#     # ... (código do modelo)
#
# class Auditoria(models.Model):
#     # ... (código do modelo)
#
# class Backup(models.Model):
#     # ... (código do modelo)
#
# class Notificacao(models.Model):
#     # ... (código do modelo)
#