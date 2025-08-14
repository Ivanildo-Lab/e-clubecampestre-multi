from django.db import models
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from financeiro.models import Mensalidade
from socios.models import Socio
import uuid

Usuario = get_user_model()


class TemplateCobranca(models.Model):
    TIPO_TEMPLATE_CHOICES = [
        ('EMAIL', 'E-mail'),
        ('SMS', 'SMS'),
        ('WHATSAPP', 'WhatsApp'),
        ('CARTA', 'Carta'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome do Template'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_TEMPLATE_CHOICES,
        verbose_name='Tipo de Template'
    )
    
    assunto = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Assunto'
    )
    
    template = models.TextField(
        verbose_name='Template'
    )
    
    variaveis_disponiveis = models.TextField(
        blank=True,
        null=True,
        verbose_name='Variáveis Disponíveis',
        help_text='Lista de variáveis que podem ser usadas no template'
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
        verbose_name = 'Template de Cobrança'
        verbose_name_plural = 'Templates de Cobrança'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"
    
    def render_template(self, contexto):
        """Renderiza o template com o contexto fornecido"""
        try:
            from django.template import Template, Context
            template = Template(self.template)
            context = Context(contexto)
            return template.render(context)
        except Exception as e:
            return f"Erro ao renderizar template: {str(e)}"


class CampanhaCobranca(models.Model):
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('ATIVO', 'Ativo'),
        ('PAUSADO', 'Pausado'),
        ('FINALIZADO', 'Finalizado'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome da Campanha'
    )
    
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    template = models.ForeignKey(
        TemplateCobranca,
        on_delete=models.PROTECT,
        related_name='campanhas',
        verbose_name='Template'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name='Status'
    )
    
    data_inicio = models.DateTimeField(
        verbose_name='Data de Início'
    )
    
    data_fim = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Fim'
    )
    
    destinatarios = models.ManyToManyField(
        Socio,
        blank=True,
        related_name='campanhas_recebidas',
        verbose_name='Destinatários'
    )
    
    filtro_status_mensalidade = models.CharField(
        max_length=20,
        choices=Mensalidade.STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name='Filtrar por Status da Mensalidade'
    )
    
    filtro_dias_atraso = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Filtrar por Dias de Atraso'
    )
    
    total_envios = models.IntegerField(
        default=0,
        verbose_name='Total de Envios'
    )
    
    total_sucesso = models.IntegerField(
        default=0,
        verbose_name='Total de Sucessos'
    )
    
    total_falhas = models.IntegerField(
        default=0,
        verbose_name='Total de Falhas'
    )
    
    criado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='campanhas_criadas',
        verbose_name='Criado por'
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
        verbose_name = 'Campanha de Cobrança'
        verbose_name_plural = 'Campanhas de Cobrança'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return self.nome
    
    def get_destinatarios_filtrados(self):
        """Retorna os destinatários filtrados conforme os critérios da campanha"""
        destinatarios = self.destinatarios.all()
        
        if self.filtro_status_mensalidade:
            socios_com_mensalidade_filtrada = Socio.objects.filter(
                mensalidades__status=self.filtro_status_mensalidade
            ).distinct()
            
            if self.destinatarios.exists():
                destinatarios = destinatarios.filter(
                    id__in=socios_com_mensalidade_filtrada
                )
            else:
                destinatarios = socios_com_mensalidade_filtrada
        
        return destinatarios


class EnvioCobranca(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ENVIADO', 'Enviado'),
        ('FALHA', 'Falha'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    campanha = models.ForeignKey(
        CampanhaCobranca,
        on_delete=models.CASCADE,
        related_name='envios',
        verbose_name='Campanha'
    )
    
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='envios_cobranca',
        verbose_name='Sócio'
    )
    
    mensalidade = models.ForeignKey(
        Mensalidade,
        on_delete=models.CASCADE,
        related_name='envios_cobranca',
        verbose_name='Mensalidade'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    
    conteudo_enviado = models.TextField(
        blank=True,
        null=True,
        verbose_name='Conteúdo Enviado'
    )
    
    data_envio = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Envio'
    )
    
    data_leitura = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Leitura'
    )
    
    resposta = models.TextField(
        blank=True,
        null=True,
        verbose_name='Resposta'
    )
    
    erro = models.TextField(
        blank=True,
        null=True,
        verbose_name='Erro'
    )
    
    tentativas = models.IntegerField(
        default=0,
        verbose_name='Tentativas'
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
        verbose_name = 'Envio de Cobrança'
        verbose_name_plural = 'Envios de Cobrança'
        ordering = ['-data_criacao']
        unique_together = ['campanha', 'socio', 'mensalidade']
    
    def __str__(self):
        return f"{self.campanha.nome} - {self.socio.nome_completo}"
    
    def enviar_email(self):
        """Envia a cobrança por e-mail"""
        try:
            contexto = {
                'socio': self.socio,
                'mensalidade': self.mensalidade,
                'campanha': self.campanha,
            }
            
            conteudo = self.campanha.template.render_template(contexto)
            
            send_mail(
                subject=self.campanha.template.assunto,
                message=conteudo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.socio.email],
                fail_silently=False,
            )
            
            self.conteudo_enviado = conteudo
            self.status = 'ENVIADO'
            self.data_envio = timezone.now()
            self.save()
            
            return True
            
        except Exception as e:
            self.erro = str(e)
            self.status = 'FALHA'
            self.save()
            return False


class HistoricoCobranca(models.Model):
    ACAO_CHOICES = [
        ('ENVIO_COBRANCA', 'Envio de Cobrança'),
        ('CONTATO_TELEFONICO', 'Contato Telefônico'),
        ('VISITA', 'Visita'),
        ('NEGOCIACAO', 'Negociação'),
        ('PAGAMENTO', 'Pagamento'),
        ('ACORDO', 'Acordo'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='historico_cobranca',
        verbose_name='Sócio'
    )
    
    mensalidade = models.ForeignKey(
        Mensalidade,
        on_delete=models.CASCADE,
        related_name='historico_cobranca',
        verbose_name='Mensalidade'
    )
    
    acao = models.CharField(
        max_length=20,
        choices=ACAO_CHOICES,
        verbose_name='Ação'
    )
    
    descricao = models.TextField(
        verbose_name='Descrição'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='historico_cobranca_registrado',
        verbose_name='Usuário'
    )
    
    data_acao = models.DateTimeField(
        verbose_name='Data da Ação'
    )
    
    proximo_passo = models.TextField(
        blank=True,
        null=True,
        verbose_name='Próximo Passo'
    )
    
    data_proximo_passo = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data do Próximo Passo'
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
        verbose_name = 'Histórico de Cobrança'
        verbose_name_plural = 'Históricos de Cobrança'
        ordering = ['-data_acao']
    
    def __str__(self):
        return f"{self.socio.nome_completo} - {self.get_acao_display()}"