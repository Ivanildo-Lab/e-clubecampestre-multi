from django.db import models
from django.utils import timezone
from core.models import Empresa


class CategoriaProduto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='categorias_produto')
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descricao")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        unique_together = ('empresa', 'nome')
        ordering = ['nome']


class Produto(models.Model):
    class UnidadeChoices(models.TextChoices):
        UN = 'UN', 'Unidade'
        KG = 'KG', 'Quilograma'
        L = 'L', 'Litro'
        M = 'M', 'Metro'
        CX = 'CX', 'Caixa'
        PC = 'PC', 'Peca'

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='produtos')
    categoria = models.ForeignKey(
        CategoriaProduto, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='produtos', verbose_name="Categoria"
    )
    nome = models.CharField(max_length=255, verbose_name="Nome do Produto")
    descricao = models.TextField(blank=True, verbose_name="Descricao")
    codigo_barras = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Codigo de Barras")
    unidade = models.CharField(
        max_length=5, choices=UnidadeChoices.choices,
        default=UnidadeChoices.UN, verbose_name="Unidade de Medida"
    )
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Preco de Custo (R$)")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Preco de Venda (R$)")
    estoque_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Estoque Atual")
    estoque_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Estoque Minimo")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} (Estoque: {self.estoque_atual} {self.get_unidade_display()})"

    @property
    def estoque_baixo(self):
        return self.estoque_atual <= self.estoque_minimo

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']


class MovimentacaoEstoque(models.Model):
    class TipoChoices(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SAIDA = 'SAIDA', 'Saida'
        AJUSTE = 'AJUSTE', 'Ajuste'

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='movimentacoes_estoque')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=10, choices=TipoChoices.choices, verbose_name="Tipo de Movimentacao")
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantidade")
    fornecedor = models.ForeignKey(
        'fornecedores.Fornecedor', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Fornecedor", related_name='movimentacoes_estoque'
    )
    valor_compra = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Valor Total da Compra (R$)"
    )
    motivo = models.CharField(max_length=255, verbose_name="Motivo")
    data_movimentacao = models.DateTimeField(default=timezone.now, verbose_name="Data da Movimentacao")
    usuario = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.SET_NULL, null=True,
        verbose_name="Usuario Responsavel"
    )
    observacao = models.TextField(blank=True, verbose_name="Observacao")

    def __str__(self):
        return f"{self.tipo} - {self.produto.nome} ({self.quantidade})"

    class Meta:
        verbose_name = "Movimentacao de Estoque"
        verbose_name_plural = "Movimentacoes de Estoque"
        ordering = ['-data_movimentacao']
