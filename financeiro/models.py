# financeiro/models.py

from django.db import models
from django.utils import timezone
import datetime
from core.models import Socio # Importamos o Sócio para criar o relacionamento
from django.db import transaction


class MensalidadeManager(models.Manager):
    def atualizar_status_atrasadas(self):
        # ... (esta função continua a mesma) ...
        hoje = timezone.now().date()
        mensalidades_vencidas = self.get_queryset().filter(status='PENDENTE', data_vencimento__lt=hoje)
        num_atualizadas = mensalidades_vencidas.update(status='ATRASADA')
        return num_atualizadas

    def gerar_mensalidades_para_ativos(self):
        """
        Lógica centralizada para gerar mensalidades.
        Retorna uma tupla: (num_criadas, num_ignoradas)
        """
        hoje = datetime.date.today()
        competencia = hoje.replace(day=1)
        
        socios_ativos = Socio.objects.filter(situacao=Socio.Situacao.ATIVO).select_related('categoria')
        socios_com_mensalidade = self.get_queryset().filter(competencia=competencia).values_list('socio_id', flat=True)
        socios_para_gerar = socios_ativos.exclude(id__in=socios_com_mensalidade)
        
        if not socios_para_gerar.exists():
            return (0, 0) # Retorna 0 criadas, 0 ignoradas

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

    # Conecta nosso manager customizado ao modelo
    objects = MensalidadeManager()

    def __str__(self):
        return f"Mensalidade de {self.socio.nome} - {self.competencia.strftime('%m/%Y')}"

    class Meta:
        verbose_name = "Mensalidade"
        verbose_name_plural = "Mensalidades"
        unique_together = ('socio', 'competencia')


class CategoriaTransacao(models.Model):
    """ Ex: 'Taxa de Evento', 'Aluguel de Quiosque', 'Salários', 'Manutenção' """
    nome = models.CharField(max_length=100, unique=True)
    TIPO_CHOICES = [('RECEITA', 'Receita'), ('DESPESA', 'Despesa')]
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Transação"
        verbose_name_plural = "Categorias de Transações"

class Transacao(models.Model):
    """ Modelo genérico para Receitas e Despesas Avulsas """
    categoria = models.ForeignKey(CategoriaTransacao, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_transacao = models.DateField(default=timezone.now)
    socio = models.ForeignKey(Socio, on_delete=models.SET_NULL, blank=True, null=True, help_text="Opcional, se a transação for ligada a um sócio específico")
    
    def __str__(self):
        return f"{self.categoria.get_tipo_display()}: {self.descricao} - R${self.valor}"

    class Meta:
        verbose_name = "Transação Avulsa"
        verbose_name_plural = "Transações Avulsas"
        ordering = ['-data_transacao']
