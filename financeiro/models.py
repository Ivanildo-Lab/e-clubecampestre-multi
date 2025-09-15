# financeiro/models.py

from django.db import models
from django.utils import timezone
from django.db import transaction
import datetime

# Importa os modelos do app 'core' de forma segura para evitar erros
from core.models import Socio, Empresa 

# Manager customizado para a lógica de negócio das mensalidades
class MensalidadeManager(models.Manager):
    def atualizar_status_atrasadas(self):
        """
        Encontra todas as mensalidades pendentes que já venceram e
        atualiza seu status para 'ATRASADA'.
        """
        hoje = timezone.now().date()
        mensalidades_vencidas = self.get_queryset().filter(
            status='PENDENTE',
            data_vencimento__lt=hoje
        )
        mensalidades_vencidas.update(status='ATRASADA')

    def gerar_mensalidades_para_ativos(self, empresa_id):
        """
        Lógica centralizada para gerar mensalidades para uma empresa específica.
        Retorna uma tupla: (num_criadas, num_ignoradas)
        """
        hoje = datetime.date.today()
        competencia = hoje.replace(day=1)
        
        # Filtra sócios ativos DA EMPRESA ESPECÍFICA
        socios_ativos = Socio.objects.filter(
            empresa_id=empresa_id,
            situacao=Socio.Situacao.ATIVO
        ).select_related('categoria')

        socios_com_mensalidade = self.get_queryset().filter(
            socio__empresa_id=empresa_id,
            competencia=competencia
        ).values_list('socio_id', flat=True)

        socios_para_gerar = socios_ativos.exclude(id__in=socios_com_mensalidade)
        
        if not socios_para_gerar.exists():
            return (0, 0)

        novas_mensalidades = []
        num_ignoradas = 0

        for socio in socios_para_gerar:
            valor = socio.categoria.valor_mensalidade
            dia_vencimento = socio.categoria.dia_vencimento

            if valor <= 0:
                num_ignoradas += 1
                continue
            
            try:
                vencimento = competencia.replace(day=dia_vencimento)
            except ValueError:
                import calendar
                ultimo_dia = calendar.monthrange(competencia.year, competencia.month)[1]
                vencimento = competencia.replace(day=ultimo_dia)

            novas_mensalidades.append(Mensalidade(
                socio=socio, competencia=competencia, valor=valor, data_vencimento=vencimento
            ))

        if novas_mensalidades:
            with transaction.atomic():
                self.bulk_create(novas_mensalidades)
        
        return (len(novas_mensalidades), num_ignoradas)

# Modelo de Mensalidade
class Mensalidade(models.Model):
    class StatusChoice(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        PAGA = 'PAGA', 'Paga'
        ATRASADA = 'ATRASADA', 'Atrasada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    socio = models.ForeignKey(Socio, on_delete=models.PROTECT, related_name='mensalidades')
    competencia = models.DateField(verbose_name="Mês de Competência")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=StatusChoice.choices, default=StatusChoice.PENDENTE)
    
    objects = MensalidadeManager()

    def __str__(self):
        return f"Mensalidade de {self.socio.nome} - {self.competencia.strftime('%m/%Y')}"
    class Meta:
        verbose_name = "Mensalidade"
        verbose_name_plural = "Mensalidades"
        unique_together = ('socio', 'competencia')

# Modelos de Categoria de Transação e Transação
class CategoriaTransacao(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    TIPO_CHOICES = [('RECEITA', 'Receita'), ('DESPESA', 'Despesa')]
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Categoria de Transação"
        verbose_name_plural = "Categorias de Transações"
        unique_together = ('empresa', 'nome')

class Transacao(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaTransacao, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_transacao = models.DateField(default=timezone.now)
    socio = models.ForeignKey(Socio, on_delete=models.SET_NULL, blank=True, null=True, help_text="Opcional")
    
    def __str__(self):
        return f"{self.categoria.get_tipo_display()}: {self.descricao} - R${self.valor}"
    class Meta:
        verbose_name = "Transação Avulsa"
        verbose_name_plural = "Transações Avulsas"
        ordering = ['-data_transacao']