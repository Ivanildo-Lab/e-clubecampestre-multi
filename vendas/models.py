from django.db import models
from django.utils import timezone
from django.db import transaction
from django.conf import settings


class Venda(models.Model):
    class TipoChoices(models.TextChoices):
        A_VISTA = 'A_VISTA', 'A Vista'
        A_PRAZO = 'A_PRAZO', 'A Prazo (Conta do Socio)'

    class StatusChoices(models.TextChoices):
        CONCLUIDA = 'CONCLUIDA', 'Concluida'
        CANCELADA = 'CANCELADA', 'Cancelada'

    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='vendas')
    socio = models.ForeignKey(
        'core.Socio', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vendas', verbose_name="Socio Cliente"
    )
    data_venda = models.DateTimeField(default=timezone.now, verbose_name="Data da Venda")
    tipo = models.CharField(max_length=10, choices=TipoChoices.choices, verbose_name="Tipo de Venda")
    forma_pagamento = models.ForeignKey(
        'formas_pagamento.FormaPagamento', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Forma de Pagamento"
    )
    caixa = models.ForeignKey(
        'financeiro.Caixa', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Caixa"
    )
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Total")
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices,
        default=StatusChoices.CONCLUIDA, verbose_name="Status"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name="Usuario Responsavel"
    )
    observacao = models.TextField(blank=True, verbose_name="Observacao")

    def __str__(self):
        socio_nome = self.socio.nome if self.socio else 'Consumidor Final'
        return f"Venda #{self.pk} - {socio_nome} - R$ {self.valor_total}"

    def _get_plano_vendas(self):
        from financeiro.models import PlanoDeContas
        from core.models import ConfiguracaoSistema
        # 1. Prioridade: configuracao explicita
        try:
            cfg = ConfiguracaoSistema.objects.filter(
                empresa=self.empresa, chave='PLANO_CONTAS_VENDAS_ID'
            ).first()
            if cfg and cfg.valor:
                plano_cfg = PlanoDeContas.objects.filter(
                    empresa=self.empresa, id=int(cfg.valor), aceita_lancamentos=True
                ).first()
                if plano_cfg:
                    return plano_cfg
        except Exception:
            pass
        # 2. Busca por nome contendo VENDA
        plano = PlanoDeContas.objects.filter(
            empresa=self.empresa, tipo='RECEITA',
            nome__icontains='VENDA', aceita_lancamentos=True
        ).order_by('codigo').first()
        # 3. Fallback generico RECEITA
        if not plano:
            plano = PlanoDeContas.objects.filter(
                empresa=self.empresa, tipo='RECEITA', aceita_lancamentos=True
            ).order_by('codigo').first()
        return plano

    def confirmar(self):
        from estoque.models import MovimentacaoEstoque
        from financeiro.models import LancamentoCaixa, Conta

        if self.status == self.StatusChoices.CANCELADA:
            return False

        with transaction.atomic():
            for item in self.itens.select_related('produto').all():
                if item.produto.estoque_atual < item.quantidade:
                    raise ValueError(
                        f"Estoque insuficiente para '{item.produto.nome}'. "
                        f"Disponivel: {item.produto.estoque_atual}"
                    )
                item.produto.estoque_atual -= item.quantidade
                item.produto.save(update_fields=['estoque_atual'])

                MovimentacaoEstoque.objects.create(
                    empresa=self.empresa,
                    produto=item.produto,
                    tipo=MovimentacaoEstoque.TipoChoices.SAIDA,
                    quantidade=item.quantidade,
                    motivo=f"Venda #{self.pk}",
                    usuario=self.usuario,
                )

            socio_nome = self.socio.nome if self.socio else 'Consumidor Final'
            plano = self._get_plano_vendas()

            if self.tipo == self.TipoChoices.A_VISTA and self.caixa:
                LancamentoCaixa.objects.create(
                    empresa=self.empresa,
                    caixa=self.caixa,
                    data_lancamento=self.data_venda.date(),
                    descricao=f"Venda #{self.pk} - {socio_nome}",
                    valor=self.valor_total,
                    plano_de_contas=plano,
                )
            elif self.tipo == self.TipoChoices.A_PRAZO and self.socio:
                Conta.objects.create(
                    empresa=self.empresa,
                    plano_de_contas=plano,
                    socio=self.socio,
                    descricao=f"Venda #{self.pk} - {socio_nome}",
                    valor=self.valor_total,
                    data_vencimento=self.data_venda.date(),
                    status='PENDENTE',
                )

        return True

    def cancelar(self):
        from estoque.models import MovimentacaoEstoque
        from financeiro.models import LancamentoCaixa, Conta

        if self.status == self.StatusChoices.CANCELADA:
            return False

        with transaction.atomic():
            for item in self.itens.select_related('produto').all():
                item.produto.estoque_atual += item.quantidade
                item.produto.save(update_fields=['estoque_atual'])

                MovimentacaoEstoque.objects.create(
                    empresa=self.empresa,
                    produto=item.produto,
                    tipo=MovimentacaoEstoque.TipoChoices.ENTRADA,
                    quantidade=item.quantidade,
                    motivo=f"Estorno da Venda #{self.pk}",
                    usuario=self.usuario,
                )

            LancamentoCaixa.objects.filter(
                descricao__contains=f"Venda #{self.pk}"
            ).delete()

            Conta.objects.filter(
                descricao__contains=f"Venda #{self.pk}"
            ).delete()

            self.status = self.StatusChoices.CANCELADA
            self.save(update_fields=['status'])

        return True

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-data_venda']


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('estoque.Produto', on_delete=models.PROTECT, verbose_name="Produto")
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preco Unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} - R$ {self.subtotal}"

    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"
