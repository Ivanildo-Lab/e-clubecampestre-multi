from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from socios.models import Socio
import uuid

Usuario = get_user_model()


class PlanoMensalidade(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome do Plano'
    )
    
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
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
        verbose_name = 'Plano de Mensalidade'
        verbose_name_plural = 'Planos de Mensalidade'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"


class Mensalidade(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('ATRASADO', 'Atrasado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('TRANSFERENCIA', 'Transferência Bancária'),
        ('PIX', 'PIX'),
        ('BOLETO', 'Boleto'),
        ('CHEQUE', 'Cheque'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='mensalidades',
        verbose_name='Sócio'
    )
    
    plano = models.ForeignKey(
        PlanoMensalidade,
        on_delete=models.PROTECT,
        related_name='mensalidades',
        verbose_name='Plano'
    )
    
    referencia = models.CharField(
        max_length=7,
        verbose_name='Referência (MM/AAAA)'
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )
    
    data_vencimento = models.DateField(
        verbose_name='Data de Vencimento'
    )
    
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Pagamento'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        blank=True,
        null=True,
        verbose_name='Forma de Pagamento'
    )
    
    comprovante = models.FileField(
        upload_to='financeiro/comprovantes/',
        blank=True,
        null=True,
        verbose_name='Comprovante'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Desconto'
    )
    
    juros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Juros'
    )
    
    valor_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Valor Pago'
    )
    
    gerado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mensalidades_geradas',
        verbose_name='Gerado por'
    )
    
    pago_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mensalidades_pagas',
        verbose_name='Pago por'
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
        verbose_name = 'Mensalidade'
        verbose_name_plural = 'Mensalidades'
        ordering = ['-data_vencimento']
        unique_together = ['socio', 'referencia']
    
    def __str__(self):
        return f"{self.socio.nome_completo} - {self.referencia} - R$ {self.valor}"
    
    def clean(self):
        if self.data_pagamento and self.data_pagamento > self.data_vencimento:
            # Calcular juros simples de 1% ao mês
            dias_atraso = (self.data_pagamento - self.data_vencimento).days
            meses_atraso = dias_atraso / 30
            self.juros = self.valor * 0.01 * meses_atraso
        
        if self.valor_pago is None and self.status == 'PAGO':
            self.valor_pago = self.valor + self.juros - self.desconto
        
        if self.status == 'PAGO' and not self.data_pagamento:
            raise ValidationError({'data_pagamento': 'Data de pagamento é obrigatória para mensalidades pagas.'})
        
        if self.status == 'PAGO' and not self.forma_pagamento:
            raise ValidationError({'forma_pagamento': 'Forma de pagamento é obrigatória para mensalidades pagas.'})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def dias_atraso(self):
        if self.status in ['PENDENTE', 'ATRASADO'] and self.data_vencimento:
            from datetime import date
            hoje = date.today()
            if hoje > self.data_vencimento:
                return (hoje - self.data_vencimento).days
        return 0
    
    @property
    def valor_total(self):
        return self.valor + self.juros - self.desconto


class CategoriaReceita(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome da Categoria'
    )
    
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
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
        verbose_name = 'Categoria de Receita'
        verbose_name_plural = 'Categorias de Receita'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Receita(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('RECEBIDO', 'Recebido'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    descricao = models.CharField(
        max_length=200,
        verbose_name='Descrição'
    )
    
    categoria = models.ForeignKey(
        CategoriaReceita,
        on_delete=models.PROTECT,
        related_name='receitas',
        verbose_name='Categoria'
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )
    
    data_prevista = models.DateField(
        verbose_name='Data Prevista'
    )
    
    data_recebimento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Recebimento'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    
    forma_recebimento = models.CharField(
        max_length=20,
        choices=Mensalidade.FORMA_PAGAMENTO_CHOICES,
        blank=True,
        null=True,
        verbose_name='Forma de Recebimento'
    )
    
    comprovante = models.FileField(
        upload_to='financeiro/comprovantes_receitas/',
        blank=True,
        null=True,
        verbose_name='Comprovante'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='receitas_cadastradas',
        verbose_name='Usuário'
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
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'
        ordering = ['-data_prevista']
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"


class CategoriaDespesa(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome da Categoria'
    )
    
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
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
        verbose_name = 'Categoria de Despesa'
        verbose_name_plural = 'Categorias de Despesa'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Despesa(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    descricao = models.CharField(
        max_length=200,
        verbose_name='Descrição'
    )
    
    categoria = models.ForeignKey(
        CategoriaDespesa,
        on_delete=models.PROTECT,
        related_name='despesas',
        verbose_name='Categoria'
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )
    
    data_vencimento = models.DateField(
        verbose_name='Data de Vencimento'
    )
    
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Pagamento'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    
    forma_pagamento = models.CharField(
        max_length=20,
        choices=Mensalidade.FORMA_PAGAMENTO_CHOICES,
        blank=True,
        null=True,
        verbose_name='Forma de Pagamento'
    )
    
    comprovante = models.FileField(
        upload_to='financeiro/comprovantes_despesas/',
        blank=True,
        null=True,
        verbose_name='Comprovante'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='despesas_cadastradas',
        verbose_name='Usuário'
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
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data_vencimento']
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"