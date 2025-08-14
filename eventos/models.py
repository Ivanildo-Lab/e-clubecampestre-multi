from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from socios.models import Socio
import uuid

Usuario = get_user_model()


class Evento(models.Model):
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('PUBLICADO', 'Publicado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TIPO_EVENTO_CHOICES = [
        ('SOCIAL', 'Social'),
        ('ESPORTIVO', 'Esportivo'),
        ('CULTURAL', 'Cultural'),
        ('FAMILIAR', 'Familiar'),
        ('EMPRESARIAL', 'Empresarial'),
        ('OUTRO', 'Outro'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome do Evento'
    )
    
    descricao = models.TextField(
        verbose_name='Descrição'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        verbose_name='Tipo de Evento'
    )
    
    data_inicio = models.DateTimeField(
        verbose_name='Data de Início'
    )
    
    data_fim = models.DateTimeField(
        verbose_name='Data de Fim'
    )
    
    local = models.CharField(
        max_length=200,
        verbose_name='Local'
    )
    
    endereco = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Endereço Completo'
    )
    
    capacidade_maxima = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Capacidade Máxima'
    )
    
    valor_ingresso_socio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Valor do Ingresso (Sócio)'
    )
    
    valor_ingresso_convidado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Valor do Ingresso (Convidado)'
    )
    
    permite_convidados = models.BooleanField(
        default=True,
        verbose_name='Permite Convidados'
    )
    
    max_convidados_por_socio = models.IntegerField(
        default=2,
        verbose_name='Máximo de Convidados por Sócio'
    )
    
    imagem = models.ImageField(
        upload_to='eventos/imagens/',
        blank=True,
        null=True,
        verbose_name='Imagem do Evento'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name='Status'
    )
    
    inscricoes_abertas = models.BooleanField(
        default=True,
        verbose_name='Inscrições Abertas'
    )
    
    requer_confirmacao = models.BooleanField(
        default=False,
        verbose_name='Requer Confirmação'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    organizador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_organizados',
        verbose_name='Organizador'
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
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return self.nome
    
    def clean(self):
        if self.data_fim <= self.data_inicio:
            raise ValidationError({'data_fim': 'A data de fim deve ser posterior à data de início.'})
        
        if self.valor_ingresso_convidado < self.valor_ingresso_socio:
            raise ValidationError({
                'valor_ingresso_convidado': 'O valor para convidados não pode ser menor que o valor para sócios.'
            })
    
    @property
    def total_inscritos(self):
        return self.inscricoes.filter(status='CONFIRMADO').count()
    
    @property
    def total_convidados(self):
        return self.inscricoes.filter(status='CONFIRMADO').aggregate(
            total=models.Sum('quantidade_convidados')
        )['total'] or 0
    
    @property
    def vagas_disponiveis(self):
        if self.capacidade_maxima:
            ocupadas = self.total_inscritos + self.total_convidados
            return max(0, self.capacidade_maxima - ocupadas)
        return None
    
    @property
    def esta_inscricao_aberta(self):
        from django.utils import timezone
        return (
            self.inscricoes_abertas and 
            self.status in ['PUBLICADO', 'EM_ANDAMENTO'] and
            self.data_inicio > timezone.now()
        )


class InscricaoEvento(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
        ('NAO_COMPARECEU', 'Não Compareceu'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='inscricoes',
        verbose_name='Evento'
    )
    
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='inscricoes_eventos',
        verbose_name='Sócio'
    )
    
    quantidade_convidados = models.IntegerField(
        default=0,
        verbose_name='Quantidade de Convidados'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    
    data_inscricao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Inscrição'
    )
    
    data_confirmacao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Confirmação'
    )
    
    data_cancelamento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Cancelamento'
    )
    
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Valor Total'
    )
    
    forma_pagamento = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Forma de Pagamento'
    )
    
    pago = models.BooleanField(
        default=False,
        verbose_name='Pago'
    )
    
    data_pagamento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Pagamento'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    usuario_cadastro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inscricoes_cadastradas',
        verbose_name='Usuário Cadastro'
    )
    
    class Meta:
        verbose_name = 'Inscrição em Evento'
        verbose_name_plural = 'Inscrições em Eventos'
        ordering = ['-data_inscricao']
        unique_together = ['evento', 'socio']
    
    def __str__(self):
        return f"{self.socio.nome_completo} - {self.evento.nome}"
    
    def clean(self):
        if not self.evento.permite_convidados and self.quantidade_convidados > 0:
            raise ValidationError({
                'quantidade_convidados': 'Este evento não permite convidados.'
            })
        
        if self.quantidade_convidados > self.evento.max_convidados_por_socio:
            raise ValidationError({
                'quantidade_convidados': f'O máximo de convidados por sócio é {self.evento.max_convidados_por_socio}.'
            })
        
        # Verificar capacidade máxima
        if self.evento.capacidade_maxima:
            total_atual = self.evento.total_inscritos + self.evento.total_convidados
            if self.status == 'CONFIRMADO':
                total_inscricao = 1 + self.quantidade_convidados
                if total_atual + total_inscricao > self.evento.capacidade_maxima:
                    raise ValidationError('Não há vagas disponíveis para este evento.')
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Calcular valor total
        if self.evento:
            valor_socio = self.evento.valor_ingresso_socio
            valor_convidado = self.evento.valor_ingresso_convidado * self.quantidade_convidados
            self.valor_total = valor_socio + valor_convidado
        
        super().save(*args, **kwargs)
    
    @property
    def total_pessoas(self):
        return 1 + self.quantidade_convidados


class ConvidadoEvento(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    inscricao = models.ForeignKey(
        InscricaoEvento,
        on_delete=models.CASCADE,
        related_name='convidados',
        verbose_name='Inscrição'
    )
    
    nome_completo = models.CharField(
        max_length=200,
        verbose_name='Nome Completo'
    )
    
    documento = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Documento (RG/CPF)'
    )
    
    data_nascimento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Nascimento'
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='E-mail'
    )
    
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefone'
    )
    
    parentesco = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Parentesco'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    compareceu = models.BooleanField(
        default=False,
        verbose_name='Compareceu'
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
        verbose_name = 'Convidado de Evento'
        verbose_name_plural = 'Convidados de Eventos'
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"{self.nome_completo} - {self.inscricao.evento.nome}"


class CheckinEvento(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='checkins',
        verbose_name='Evento'
    )
    
    inscricao = models.ForeignKey(
        InscricaoEvento,
        on_delete=models.CASCADE,
        related_name='checkins',
        verbose_name='Inscrição'
    )
    
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='checkins_eventos',
        verbose_name='Sócio'
    )
    
    data_checkin = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data do Check-in'
    )
    
    usuario_checkin = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='checkins_realizados',
        verbose_name='Usuário Check-in'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    class Meta:
        verbose_name = 'Check-in de Evento'
        verbose_name_plural = 'Check-ins de Eventos'
        ordering = ['-data_checkin']
        unique_together = ['evento', 'socio']
    
    def __str__(self):
        return f"{self.socio.nome_completo} - {self.evento.nome}"