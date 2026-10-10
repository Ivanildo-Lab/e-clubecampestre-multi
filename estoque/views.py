from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Sum, F
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from decimal import Decimal

from .models import Produto, CategoriaProduto, MovimentacaoEstoque
from .forms import ProdutoForm, CategoriaProdutoForm, MovimentacaoEstoqueForm
from core.models import Empresa


class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = 'estoque/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 20

    def get_queryset(self):
        queryset = Produto.objects.filter(empresa=self.request.user.empresa)

        search_query = self.request.GET.get('q')
        categoria_id = self.request.GET.get('categoria')
        estoque_baixo = self.request.GET.get('estoque_baixo')

        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) | Q(codigo_barras__icontains=search_query)
            )
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if estoque_baixo == '1':
            queryset = queryset.filter(controla_estoque=True, estoque_atual__lte=F('estoque_minimo'))

        return queryset.select_related('categoria').order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        context['titulo_pagina'] = 'Produtos'
        context['categorias'] = CategoriaProduto.objects.filter(empresa=empresa_atual)
        context['search_query'] = self.request.GET.get('q', '')
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['estoque_baixo_filtro'] = self.request.GET.get('estoque_baixo', '')
        context['total_produtos'] = Produto.objects.filter(empresa=empresa_atual).count()
        context['produtos_estoque_baixo'] = Produto.objects.filter(
            empresa=empresa_atual, controla_estoque=True,
            estoque_atual__lte=F('estoque_minimo'), ativo=True
        ).count()
        return context


class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'estoque/produto_form.html'
    success_url = reverse_lazy('estoque:lista_produtos')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        messages.success(self.request, 'Produto cadastrado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Adicionar Produto'
        return context


class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'estoque/produto_form.html'
    success_url = reverse_lazy('estoque:lista_produtos')

    def get_queryset(self):
        return Produto.objects.filter(empresa=self.request.user.empresa)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Produto'
        return context


class ProdutoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        produto = get_object_or_404(Produto, pk=pk, empresa=request.user.empresa)
        try:
            nome = produto.nome
            produto.delete()
            messages.success(request, f'O produto "{nome}" foi excluido com sucesso.')
        except Exception as e:
            messages.error(request, f'Nao foi possivel excluir o produto "{produto.nome}".')
        return redirect('estoque:lista_produtos')


class MovimentacaoEstoqueCreateView(LoginRequiredMixin, CreateView):
    model = MovimentacaoEstoque
    form_class = MovimentacaoEstoqueForm
    template_name = 'estoque/movimentacao_form.html'
    success_url = reverse_lazy('estoque:lista_movimentacoes')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        form.instance.usuario = self.request.user

        with transaction.atomic():
            produto = form.cleaned_data['produto']
            tipo = form.cleaned_data['tipo']
            quantidade = form.cleaned_data['quantidade']
            valor_compra = form.cleaned_data.get('valor_compra') or Decimal('0.00')
            controla = produto.controla_estoque

            if controla and tipo == 'ENTRADA':
                estoque_anterior = produto.estoque_atual
                estoque_novo = estoque_anterior + quantidade

                if estoque_anterior > 0 and valor_compra > 0:
                    custo_total_anterior = estoque_anterior * produto.preco_custo
                    custo_total_entrada = quantidade * (valor_compra / quantidade) if quantidade > 0 else valor_compra
                    produto.preco_custo = (custo_total_anterior + custo_total_entrada) / estoque_novo
                elif valor_compra > 0 and quantidade > 0:
                    produto.preco_custo = valor_compra / quantidade

                produto.estoque_atual = estoque_novo
                produto.save()

            elif controla and tipo == 'SAIDA':
                produto.estoque_atual -= quantidade
                produto.save()

            elif controla and tipo == 'AJUSTE':
                produto.estoque_atual = quantidade
                produto.save()

            form.save()

        messages.success(self.request, f'Movimentacao registrada: {tipo} de {quantidade} {produto.get_unidade_display()} - {produto.nome}')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Movimentacao de Estoque'
        return context


class MovimentacaoEstoqueListView(LoginRequiredMixin, ListView):
    model = MovimentacaoEstoque
    template_name = 'estoque/movimentacao_list.html'
    context_object_name = 'movimentacoes'
    paginate_by = 20

    def get_queryset(self):
        queryset = MovimentacaoEstoque.objects.filter(empresa=self.request.user.empresa)

        search_query = self.request.GET.get('q')
        tipo = self.request.GET.get('tipo')
        produto_id = self.request.GET.get('produto')

        if search_query:
            queryset = queryset.filter(
                Q(produto__nome__icontains=search_query) | Q(motivo__icontains=search_query)
            )
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if produto_id:
            queryset = queryset.filter(produto_id=produto_id)

        return queryset.select_related('produto', 'usuario').order_by('-data_movimentacao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        context['titulo_pagina'] = 'Movimentacoes de Estoque'
        context['produtos'] = Produto.objects.filter(empresa=empresa_atual, ativo=True)
        context['search_query'] = self.request.GET.get('q', '')
        context['tipo_selecionado'] = self.request.GET.get('tipo', '')
        context['produto_selecionado'] = self.request.GET.get('produto', '')
        return context


class CategoriaProdutoListView(LoginRequiredMixin, ListView):
    model = CategoriaProduto
    template_name = 'estoque/categoria_list.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return CategoriaProduto.objects.filter(empresa=self.request.user.empresa).order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Categorias de Produtos'
        return context


class CategoriaProdutoCreateView(LoginRequiredMixin, CreateView):
    model = CategoriaProduto
    form_class = CategoriaProdutoForm
    template_name = 'estoque/categoria_form.html'
    success_url = reverse_lazy('estoque:lista_categorias')

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Adicionar Categoria'
        return context


class CategoriaProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = CategoriaProduto
    form_class = CategoriaProdutoForm
    template_name = 'estoque/categoria_form.html'
    success_url = reverse_lazy('estoque:lista_categorias')

    def get_queryset(self):
        return CategoriaProduto.objects.filter(empresa=self.request.user.empresa)

    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Categoria'
        return context


class CategoriaProdutoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        categoria = get_object_or_404(CategoriaProduto, pk=pk, empresa=request.user.empresa)
        try:
            nome = categoria.nome
            categoria.delete()
            messages.success(request, f'A categoria "{nome}" foi excluida com sucesso.')
        except Exception as e:
            messages.error(request, f'Nao foi possivel excluir a categoria "{categoria.nome}".')
        return redirect('estoque:lista_categorias')


class EstoquePDFView(LoginRequiredMixin, View):
    def get(self, request):
        empresa_atual = request.user.empresa
        queryset = Produto.objects.filter(empresa=empresa_atual, ativo=True)

        categoria_id = request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        produtos = queryset.select_related('categoria').order_by('nome')

        produtos_data = []
        total_valor_estoque = 0
        for p in produtos:
            ultima_mov = MovimentacaoEstoque.objects.filter(
                produto=p, tipo='ENTRADA', empresa=empresa_atual
            ).select_related('fornecedor').order_by('-data_movimentacao').first()

            fornecedor_nome = ultima_mov.fornecedor.nome if ultima_mov and ultima_mov.fornecedor else '--'
            valor_estoque = p.preco_custo * p.estoque_atual
            total_valor_estoque += valor_estoque

            produtos_data.append({
                'nome': p.nome,
                'categoria': p.categoria,
                'codigo_barras': p.codigo_barras,
                'get_unidade_display': p.get_unidade_display(),
                'fornecedor_ultimo': fornecedor_nome,
                'preco_custo': p.preco_custo,
                'preco_venda': p.preco_venda,
                'estoque_atual': p.estoque_atual,
                'estoque_minimo': p.estoque_minimo,
                'valor_estoque': valor_estoque,
                'estoque_baixo': p.estoque_baixo,
            })

        context = {
            'produtos': produtos_data,
            'empresa': empresa_atual,
            'total_valor_estoque': total_valor_estoque,
            'data_emissao': timezone.now(),
        }

        html_string = render_to_string('estoque/estoque_pdf_template.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="relatorio_estoque.pdf"'
        return response


class CardapioPublicView(View):
    """Cardápio online público (sem login), agrupado por categoria."""
    template_name = 'estoque/cardapio.html'

    def get(self, request, empresa_id):
        from django.shortcuts import render
        empresa = get_object_or_404(Empresa, pk=empresa_id)
        busca = (request.GET.get('q') or '').strip()
        qs = Produto.objects.filter(
            empresa=empresa, ativo=True, exibir_cardapio=True
        ).select_related('categoria')
        if busca:
            qs = qs.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
        produtos = list(qs.order_by('categoria__nome', 'nome'))
        grupos = []
        por_categoria = {}
        ordem_categorias = []
        sem_categoria = []
        for p in produtos:
            if p.categoria_id:
                key = p.categoria_id
                if key not in por_categoria:
                    por_categoria[key] = {'categoria': p.categoria, 'produtos': []}
                    ordem_categorias.append(key)
                por_categoria[key]['produtos'].append(p)
            else:
                sem_categoria.append(p)
        for key in sorted(ordem_categorias, key=lambda k: (por_categoria[k]['categoria'].nome or '').lower()):
            grupos.append(por_categoria[key])
        if sem_categoria:
            grupos.append({'categoria': None, 'produtos': sem_categoria})
        context = {
            'empresa': empresa,
            'grupos': grupos,
            'total_produtos': len(produtos),
            'busca': busca,
        }
        return render(request, self.template_name, context)


class CardapioQRCodeView(LoginRequiredMixin, View):
    """Página interna com o QR Code do cardápio da empresa do usuário."""
    def get(self, request):
        from django.shortcuts import render
        from django.urls import reverse
        empresa = request.user.empresa
        cardapio_url = request.build_absolute_uri(
            reverse('estoque:cardapio_publico', kwargs={'empresa_id': empresa.id})
        )
        context = {
            'titulo_pagina': 'Cardápio Online / QR Code',
            'empresa': empresa,
            'cardapio_url': cardapio_url,
        }
        return render(request, 'estoque/cardapio_qr.html', context)


def _gerar_qr_png(url):
    """Gera bytes PNG do QR Code para uma URL (sem depender de login)."""
    import qrcode
    from io import BytesIO
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


class CardapioQRImageView(LoginRequiredMixin, View):
    """Gera o PNG do QR Code que aponta para o cardápio público (uso interno)."""
    def get(self, request):
        from django.urls import reverse
        empresa = request.user.empresa
        cardapio_url = request.build_absolute_uri(
            reverse('estoque:cardapio_publico', kwargs={'empresa_id': empresa.id})
        )
        try:
            return HttpResponse(_gerar_qr_png(cardapio_url), content_type='image/png')
        except Exception as e:
            messages.error(request, f'Não foi possível gerar o QR Code: {e}')
            return redirect('estoque:cardapio_qr')


class CardapioQRPublicImageView(View):
    """PNG do QR Code público (sem login) — mesma imagem colada nas mesas."""
    def get(self, request, empresa_id):
        from django.urls import reverse
        empresa = get_object_or_404(Empresa, pk=empresa_id)
        cardapio_url = request.build_absolute_uri(
            reverse('estoque:cardapio_publico', kwargs={'empresa_id': empresa.id})
        )
        try:
            resp = HttpResponse(_gerar_qr_png(cardapio_url), content_type='image/png')
            resp['Content-Disposition'] = f'inline; filename="qrcode-cardapio-{empresa.id}.png"'
            return resp
        except Exception:
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound('QR Code indisponível')


class MovimentacaoEstoquePDFView(LoginRequiredMixin, View):
    def get_queryset(self):
        queryset = MovimentacaoEstoque.objects.filter(empresa=self.request.user.empresa)

        search_query = self.request.GET.get('q')
        tipo = self.request.GET.get('tipo')
        produto_id = self.request.GET.get('produto')

        if search_query:
            queryset = queryset.filter(
                Q(produto__nome__icontains=search_query) | Q(motivo__icontains=search_query)
            )
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if produto_id:
            queryset = queryset.filter(produto_id=produto_id)

        return queryset.select_related('produto', 'usuario', 'fornecedor').order_by('-data_movimentacao')

    def get(self, request):
        movimentacoes = self.get_queryset()

        mov_data = []
        total_entradas = 0
        total_saidas = 0
        total_valor_entradas = 0

        for mov in movimentacoes:
            valor_total = mov.valor_compra if mov.tipo == 'ENTRADA' and mov.valor_compra else 0
            mov_data.append({
                'data_movimentacao': mov.data_movimentacao,
                'produto_nome': mov.produto.nome,
                'tipo': mov.tipo,
                'tipo_display': mov.get_tipo_display(),
                'quantidade': mov.quantidade,
                'fornecedor_nome': mov.fornecedor.nome if mov.fornecedor else '--',
                'valor_compra': mov.valor_compra,
                'valor_total': valor_total,
                'motivo': mov.motivo,
                'usuario_nome': mov.usuario.get_full_name() or mov.usuario.username,
            })
            if mov.tipo == 'ENTRADA':
                total_entradas += mov.quantidade
                total_valor_entradas += valor_total
            elif mov.tipo == 'SAIDA':
                total_saidas += mov.quantidade

        filters_desc = []
        tipo_param = request.GET.get('tipo')
        produto_param = request.GET.get('produto')
        q_param = request.GET.get('q')
        if tipo_param:
            filters_desc.append(f'Tipo: {tipo_param}')
        if produto_param:
            try:
                prod = Produto.objects.get(pk=produto_param)
                filters_desc.append(f'Produto: {prod.nome}')
            except Produto.DoesNotExist:
                pass
        if q_param:
            filters_desc.append(f'Busca: {q_param}')

        context = {
            'movimentacoes': mov_data,
            'empresa': request.user.empresa,
            'data_emissao': timezone.now(),
            'total_registros': len(mov_data),
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'total_valor_entradas': total_valor_entradas,
            'filtros': ' | '.join(filters_desc) if filters_desc else 'Todos',
        }

        html_string = render_to_string('estoque/movimentacao_pdf_template.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="movimentacoes_estoque.pdf"'
        return response
