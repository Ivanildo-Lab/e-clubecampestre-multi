from django.db import models
from django.contrib.auth import get_user_model
from localflavor.br.validators import BRCPFValidator
import uuid

Usuario = get_user_model()


class Socio(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('SOLTEIRO', 'Solteiro(a)'),
        ('CASADO', 'Casado(a)'),
        ('DIVORCIADO', 'Divorciado(a)'),
        ('VIUVO', 'Viúvo(a)'),
        ('UNIAO_ESTAVEL', 'União Estável'),
    ]
    
    TIPO_SANGUINEO_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome_completo = models.CharField(
        max_length=200,
        verbose_name='Nome Completo'
    )
    
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[BRCPFValidator()],
        verbose_name='CPF'
    )
    
    rg = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='RG'
    )
    
    data_nascimento = models.DateField(
        verbose_name='Data de Nascimento'
    )
    
    estado_civil = models.CharField(
        max_length=20,
        choices=ESTADO_CIVIL_CHOICES,
        default='SOLTEIRO',
        verbose_name='Estado Civil'
    )
    
    tipo_sanguineo = models.CharField(
        max_length=3,
        choices=TIPO_SANGUINEO_CHOICES,
        blank=True,
        null=True,
        verbose_name='Tipo Sanguíneo'
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name='E-mail'
    )
    
    telefone = models.CharField(
        max_length=20,
        verbose_name='Telefone'
    )
    
    telefone_secundario = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefone Secundário'
    )
    
    endereco = models.CharField(
        max_length=200,
        verbose_name='Endereço'
    )
    
    numero = models.CharField(
        max_length=10,
        verbose_name='Número'
    )
    
    complemento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Complemento'
    )
    
    bairro = models.CharField(
        max_length=100,
        verbose_name='Bairro'
    )
    
    cidade = models.CharField(
        max_length=100,
        verbose_name='Cidade'
    )
    
    estado = models.CharField(
        max_length=2,
        verbose_name='Estado'
    )
    
    cep = models.CharField(
        max_length=9,
        verbose_name='CEP'
    )
    
    foto = models.ImageField(
        upload_to='socios/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto'
    )
    
    profissao = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Profissão'
    )
    
    empresa = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Empresa'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Cadastro'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    
    cadastrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='socios_cadastrados',
        verbose_name='Cadastrado por'
    )
    
    class Meta:
        verbose_name = 'Sócio'
        verbose_name_plural = 'Sócios'
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return self.nome_completo


class Dependente(models.Model):
    PARENTESCO_CHOICES = [
        ('CONJUGE', 'Cônjuge'),
        ('FILHO', 'Filho(a)'),
        ('ENTEADO', 'Enteado(a)'),
        ('PAI', 'Pai'),
        ('MAE', 'Mãe'),
        ('OUTRO', 'Outro'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='dependentes',
        verbose_name='Sócio Titular'
    )
    
    nome_completo = models.CharField(
        max_length=200,
        verbose_name='Nome Completo'
    )
    
    parentesco = models.CharField(
        max_length=20,
        choices=PARENTESCO_CHOICES,
        verbose_name='Parentesco'
    )
    
    data_nascimento = models.DateField(
        verbose_name='Data de Nascimento'
    )
    
    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name='CPF'
    )
    
    tipo_sanguineo = models.CharField(
        max_length=3,
        choices=Socio.TIPO_SANGUINEO_CHOICES,
        blank=True,
        null=True,
        verbose_name='Tipo Sanguíneo'
    )
    
    foto = models.ImageField(
        upload_to='socios/dependentes/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Cadastro'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    
    class Meta:
        verbose_name = 'Dependente'
        verbose_name_plural = 'Dependentes'
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"{self.nome_completo} - {self.get_parentesco_display()}"


class InteracaoSocio(models.Model):
    TIPO_INTERACAO_CHOICES = [
        ('TELEFONE', 'Telefone'),
        ('EMAIL', 'E-mail'),
        ('PRESENCIAL', 'Presencial'),
        ('WHATSAPP', 'WhatsApp'),
        ('OUTRO', 'Outro'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='interacoes',
        verbose_name='Sócio'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_INTERACAO_CHOICES,
        verbose_name='Tipo de Interação'
    )
    
    descricao = models.TextField(
        verbose_name='Descrição'
    )
    
    data_interacao = models.DateTimeField(
        verbose_name='Data da Interação'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interacoes_realizadas',
        verbose_name='Usuário'
    )
    
    proximo_contato = models.DateField(
        blank=True,
        null=True,
        verbose_name='Próximo Contato'
    )
    
    class Meta:
        verbose_name = 'Interação com Sócio'
        verbose_name_plural = 'Interações com Sócios'
        ordering = ['-data_interacao']
    
    def __str__(self):
        return f"{self.socio.nome_completo} - {self.get_tipo_display()} - {self.data_interacao.strftime('%d/%m/%Y')}"