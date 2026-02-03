# financeiro/models.py

from django.db import models
from django.utils import timezone
from django.db import transaction
import datetime
from core.models import Socio, Empresa, CategoriaSocio

# --- 1. MODELOS DE ESTRUTURA ---

class Caixa(models.Model):
    """ Representa uma conta financeira. Ex: Caixa da Secretaria, Conta Banco do Brasil """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='caixas')
    nome = models.CharField(max_length=100, verbose_name="Nome do Caixa/Conta")
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.nome} ({self.empresa.nome})"
    
    class Meta:
        verbose_name = "Caixa / Conta Bancária"
        verbose_name_plural = "Caixas / Contas Bancárias"
        unique_together = ('empresa', 'nome')

# Em financeiro/models.py

class PlanoDeContas(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='planos_de_contas')
    
    # Novo campo para o código estruturado
    codigo = models.CharField(max_length=20, verbose_name="Código")
    
    # Relacionamento pai-filho
    parent = models.ForeignKey(
        'self', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name="Conta Superior (Pai)"
    )
    
    TIPO_CHOICES = [('RECEITA', 'Receita'), ('DESPESA', 'Despesa')]
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    nome = models.CharField(max_length=100, verbose_name="Nome da Conta")
    
    # Novo campo para diferenciar contas agrupadoras das que recebem lançamentos
    aceita_lancamentos = models.BooleanField(
        default=True, 
        verbose_name="Aceita Lançamentos?",
        help_text="Marque se esta conta pode receber lançamentos diretos. Desmarque se for uma conta apenas para agrupar outras."
    )
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    class Meta:
        verbose_name = "Plano de Contas"
        verbose_name_plural = "Planos de Contas"
        # O código deve ser único por empresa
        unique_together = ('empresa', 'codigo')
        # A lista será sempre ordenada pelo código, o que cria a hierarquia visual
        ordering = ['codigo']


# --- 2. MODELOS DE "CONTAS A PAGAR/RECEBER" ---

# O Modelo MensalidadeManager e Mensalidade continuam aqui, sem alterações estruturais por enquanto
class MensalidadeManager(models.Manager):
    def atualizar_status_atrasadas(self):
        hoje = timezone.now().date()
        mensalidades_vencidas = self.get_queryset().filter(status='PENDENTE', data_vencimento__lt=hoje)
        return mensalidades_vencidas.update(status='ATRASADA')
    def gerar_mensalidades_para_ativos(self, empresa_id, convenio_id=None, meses_a_gerar=12):
        """
        Lógica para gerar mensalidades para os próximos X meses para uma empresa.
        Retorna uma tupla: (num_criadas, num_ignoradas)
        """
        hoje = datetime.date.today()
        socios_ativos = Socio.objects.filter(
            empresa_id=empresa_id,
            situacao=Socio.Situacao.ATIVO
        ).select_related('categoria')

          #Filtra por convênio, se um ID for fornecido
        if convenio_id:
            socios_ativos = socios_ativos.filter(convenio_id=convenio_id)

        if not socios_ativos.exists():
            return (0, 0)

        novas_mensalidades_para_criar = []
        num_ignoradas = 0
        num_ja_existentes = 0

        # Loop pelos próximos X meses, começando pelo mês atual
        for i in range(meses_a_gerar):
            ano_competencia = hoje.year + (hoje.month + i - 1) // 12
            mes_competencia = (hoje.month + i - 1) % 12 + 1
            competencia = datetime.date(ano_competencia, mes_competencia, 1)

            # Pega os sócios que JÁ têm mensalidade para esta competência específica
            socios_com_mensalidade = self.get_queryset().filter(
                socio__empresa_id=empresa_id,
                competencia=competencia
            ).values_list('socio_id', flat=True)
            
            socios_para_gerar_neste_mes = socios_ativos.exclude(id__in=socios_com_mensalidade)

            for socio in socios_para_gerar_neste_mes:
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

                novas_mensalidades_para_criar.append(Mensalidade(
                    socio=socio, competencia=competencia, valor=valor, data_vencimento=vencimento
                ))

        if novas_mensalidades_para_criar:
            with transaction.atomic():
                self.bulk_create(novas_mensalidades_para_criar)
        
        return (len(novas_mensalidades_para_criar), num_ignoradas)
    
    
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

class Conta(models.Model):
    """ Representa uma Conta a Pagar ou a Receber avulsa. """
    class StatusChoice(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        PAGA = 'PAGA', 'Paga'
        VENCIDA = 'VENCIDA', 'Vencida'
        CANCELADA = 'CANCELADA', 'Cancelada'
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='contas')
    plano_de_contas = models.ForeignKey(PlanoDeContas, on_delete=models.PROTECT)
    socio = models.ForeignKey(Socio, on_delete=models.SET_NULL, blank=True, null=True, help_text="Opcional")
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=StatusChoice.choices, default=StatusChoice.PENDENTE)
    fornecedor = models.ForeignKey('fornecedores.Fornecedor', on_delete=models.SET_NULL, blank=True, null=True, help_text="Opcional. Use para contas a pagar.")

    def __str__(self):
        return f"{self.plano_de_contas.get_tipo_display()}: {self.descricao}"
    class Meta:
        verbose_name = "Conta a Pagar/Receber"
        verbose_name_plural = "Contas a Pagar/Receber"

# --- 3. O CORAÇÃO DO FLUXO DE CAIXA ---

class LancamentoCaixa(models.Model):
    """ Representa um movimento real de dinheiro em um Caixa. """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='lancamentos')
    caixa = models.ForeignKey(Caixa, on_delete=models.PROTECT)
    data_lancamento = models.DateField(default=timezone.now)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=15, decimal_places=2, help_text="Use valores positivos para receitas (créditos) e negativos para despesas (débitos).")
    mensalidade_origem = models.ForeignKey(
        Mensalidade, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='lancamentos_no_caixa' # Boa prática
        ) 
    conta_origem = models.OneToOneField(Conta, on_delete=models.SET_NULL, blank=True, null=True)
    plano_de_contas = models.ForeignKey(
                        PlanoDeContas, 
                        on_delete=models.PROTECT,
                        blank=True, # Permite que o campo seja vazio nos formulários
                        null=True   # Permite que o campo seja NULO no banco de dados
                    )
    def __str__(self):
        tipo = "Crédito" if self.valor > 0 else "Débito"
        return f"{tipo} de R$ {abs(self.valor)} em {self.caixa.nome} ({self.data_lancamento})"
    class Meta:
        verbose_name = "Lançamento de Caixa"
        verbose_name_plural = "Lançamentos de Caixa"
        ordering = ['-data_lancamento']