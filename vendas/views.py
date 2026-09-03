import json
from decimal import Decimal, InvalidOperation

from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.urls import reverse_lazy

from .models import Venda, ItemVenda
from estoque.models import Produto
from financeiro.models import Caixa
from formas_pagamento.models import FormaPagamento
from core.models import Socio


class VendaPDVView(LoginRequiredMixin, View):
    template_name = 'vendas/pdv.html'

    def get(self, request):
        empresa = request.user.empresa
        produtos = Produto.objects.filter(empresa=empresa, ativo=True).select_related('categoria').order_by('nome')[:100]
        caixas = Caixa.objects.filter(empresa=empresa).order_by('nome')
        formas = FormaPagamento.objects.filter(empresa=empresa, ativo=True).order_by('nome')
        socios = Socio.objects.filter(empresa=empresa, situacao='ATIVO').order_by('nome')[:200]

        # Search filter for produtos list
        q = request.GET.get('q')
        if q:
            produtos = Produto.objects.filter(empresa=empresa, ativo=True).filter(
                Q(nome__icontains=q) | Q(codigo_barras__icontains=q)
            ).select_related('categoria').order_by('nome')[:100]
            # If AJAX request, return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                data = [
                    {
                        'id': p.id,
                        'nome': p.nome,
                        'preco_venda': str(p.preco_venda),
                        'estoque_atual': str(p.estoque_atual),
                        'unidade': p.get_unidade_display(),
                        'categoria': p.categoria.nome if p.categoria else '--',
                    }
                    for p in produtos
                ]
                return JsonResponse({'produtos': data})

        context = {
            'titulo_pagina': 'PDV - Nova Venda',
            'produtos': produtos,
            'caixas': caixas,
            'formas_pagamento': formas,
            'socios': socios,
            'search_query': q or '',
        }
        return render(request, self.template_name, context)

    def post(self, request):
        empresa = request.user.empresa
        usuario = request.user

        # Expect JSON or form-data
        try:
            if request.content_type == 'application/json':
                payload = json.loads(request.body.decode('utf-8'))
                # payload should be dict with keys tipo, caixa, etc + itens list
                if not isinstance(payload, dict):
                    raise ValueError('Payload JSON deve ser um objeto.')
            else:
                # form-data: itens_json contains JSON array string
                payload = {}
                payload_raw = request.POST.get('itens_json') or request.POST.get('itens')
                if payload_raw:
                    # Handle case where value is list-like (QueryDict returns str)
                    if isinstance(payload_raw, list):
                        payload_raw = payload_raw[0]
                    payload['itens'] = json.loads(payload_raw)
                else:
                    payload['itens'] = []
                # Populate other fields from POST
                for key in ['tipo', 'forma_pagamento', 'caixa', 'socio', 'observacao']:
                    val = request.POST.get(key)
                    if val is not None:
                        payload[key] = val
        except Exception as e:
            messages.error(request, f'Erro ao interpretar dados da venda: {e}')
            return redirect('vendas:pdv')

        tipo = payload.get('tipo')
        forma_id = payload.get('forma_pagamento')
        caixa_id = payload.get('caixa')
        socio_id = payload.get('socio')
        observacao = payload.get('observacao', '')
        itens = payload.get('itens', [])

        # Validation
        if not tipo or tipo not in ['A_VISTA', 'A_PRAZO']:
            messages.error(request, 'Selecione o tipo de venda.')
            return redirect('vendas:pdv')
        if not itens or len(itens) == 0:
            messages.error(request, 'Adicione pelo menos um produto a venda.')
            return redirect('vendas:pdv')

        if tipo == 'A_VISTA' and not caixa_id:
            messages.error(request, 'Para venda a vista, selecione o caixa.')
            return redirect('vendas:pdv')
        if tipo == 'A_PRAZO' and not socio_id:
            messages.error(request, 'Para venda a prazo, selecione o socio.')
            return redirect('vendas:pdv')

        # Resolve FKs
        caixa = None
        forma = None
        socio = None
        if caixa_id:
            try:
                caixa = Caixa.objects.get(pk=caixa_id, empresa=empresa)
            except Caixa.DoesNotExist:
                messages.error(request, 'Caixa invalido.')
                return redirect('vendas:pdv')
        if forma_id:
            try:
                forma = FormaPagamento.objects.get(pk=forma_id, empresa=empresa)
            except FormaPagamento.DoesNotExist:
                messages.error(request, 'Forma de pagamento invalida.')
                return redirect('vendas:pdv')
        if socio_id:
            try:
                socio = Socio.objects.get(pk=socio_id, empresa=empresa)
            except Socio.DoesNotExist:
                messages.error(request, 'Socio invalido.')
                return redirect('vendas:pdv')

        # Validate itens and compute total
        validated_itens = []
        valor_total = Decimal('0.00')
        for entry in itens:
            try:
                prod_id = int(entry.get('produto_id') or entry.get('produto') or entry.get('id'))
                qtd = Decimal(str(entry.get('quantidade') or entry.get('qtd') or '0'))
                # preco_unitario snapshot: use current preco_venda, but allow override
                produto = Produto.objects.get(pk=prod_id, empresa=empresa)
                preco = entry.get('preco_unitario') or entry.get('preco') or produto.preco_venda
                preco = Decimal(str(preco))
                if qtd <= 0:
                    raise ValueError('Quantidade deve ser maior que zero.')
                if preco < 0:
                    raise ValueError('Preco nao pode ser negativo.')
                if produto.estoque_atual < qtd:
                    raise ValueError(f"Estoque insuficiente para '{produto.nome}'. Disponivel: {produto.estoque_atual}")
                subtotal = qtd * preco
                validated_itens.append({
                    'produto': produto,
                    'quantidade': qtd,
                    'preco_unitario': preco,
                    'subtotal': subtotal,
                })
                valor_total += subtotal
            except Produto.DoesNotExist:
                messages.error(request, f"Produto ID {entry.get('produto_id')} nao encontrado.")
                return redirect('vendas:pdv')
            except (InvalidOperation, ValueError) as e:
                messages.error(request, str(e))
                return redirect('vendas:pdv')
            except Exception as e:
                messages.error(request, f'Erro no item: {e}')
                return redirect('vendas:pdv')

        try:
            with transaction.atomic():
                venda = Venda.objects.create(
                    empresa=empresa,
                    socio=socio,
                    tipo=tipo,
                    forma_pagamento=forma,
                    caixa=caixa,
                    valor_total=valor_total,
                    usuario=usuario,
                    observacao=observacao,
                    status=Venda.StatusChoices.CONCLUIDA,
                )
                for vi in validated_itens:
                    ItemVenda.objects.create(
                        venda=venda,
                        produto=vi['produto'],
                        quantidade=vi['quantidade'],
                        preco_unitario=vi['preco_unitario'],
                        subtotal=vi['subtotal'],
                    )
                # baixa estoque + financeiro
                venda.confirmar()

                # If AJAX JSON, return JSON
                if request.content_type == 'application/json' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'venda_id': venda.pk, 'redirect': str(reverse_lazy('vendas:detalhe', kwargs={'pk': venda.pk}))})

                messages.success(request, f'Venda #{venda.pk} registrada com sucesso! Total: R$ {valor_total:.2f}')
                return redirect('vendas:detalhe', pk=venda.pk)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('vendas:pdv')
        except Exception as e:
            messages.error(request, f'Erro ao registrar venda: {e}')
            return redirect('vendas:pdv')


class ProdutoAjaxSearchView(LoginRequiredMixin, View):
    def get(self, request):
        empresa = request.user.empresa
        q = request.GET.get('q', '').strip()
        qs = Produto.objects.filter(empresa=empresa, ativo=True)
        if q:
            qs = qs.filter(Q(nome__icontains=q) | Q(codigo_barras__icontains=q))
        qs = qs.select_related('categoria').order_by('nome')[:20]
        data = [
            {
                'id': p.id,
                'nome': p.nome,
                'preco_venda': str(p.preco_venda),
                'estoque_atual': str(p.estoque_atual),
                'unidade': p.get_unidade_display(),
                'categoria': p.categoria.nome if p.categoria else '--',
            }
            for p in qs
        ]
        return JsonResponse({'produtos': data})


class VendaListView(LoginRequiredMixin, ListView):
    model = Venda
    template_name = 'vendas/venda_list.html'
    context_object_name = 'vendas'
    paginate_by = 15

    def get_queryset(self):
        empresa = self.request.user.empresa
        qs = Venda.objects.filter(empresa=empresa).select_related('socio', 'caixa', 'forma_pagamento', 'usuario')
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')
        tipo = self.request.GET.get('tipo')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        if q:
            qs = qs.filter(Q(observacao__icontains=q) | Q(socio__nome__icontains=q) | Q(id__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if data_inicio:
            qs = qs.filter(data_venda__date__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data_venda__date__lte=data_fim)
        return qs.order_by('-data_venda')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Historico de Vendas'
        context['search_query'] = self.request.GET.get('q', '')
        context['status_filtro'] = self.request.GET.get('status', '')
        context['tipo_filtro'] = self.request.GET.get('tipo', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['status_choices'] = Venda.StatusChoices.choices
        context['tipo_choices'] = Venda.TipoChoices.choices
        return context


class VendaDetailView(LoginRequiredMixin, DetailView):
    model = Venda
    template_name = 'vendas/venda_detail.html'
    context_object_name = 'venda'

    def get_queryset(self):
        return Venda.objects.filter(empresa=self.request.user.empresa).select_related('socio', 'caixa', 'forma_pagamento', 'usuario', 'empresa').prefetch_related('itens__produto')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f"Venda #{self.object.pk}"
        return context


class VendaCancelarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        venda = get_object_or_404(Venda, pk=pk, empresa=request.user.empresa)
        if venda.status == Venda.StatusChoices.CANCELADA:
            messages.warning(request, f'Venda #{venda.pk} ja esta cancelada.')
            return redirect('vendas:detalhe', pk=venda.pk)
        try:
            venda.cancelar()
            messages.success(request, f'Venda #{venda.pk} cancelada. Estoque estornado.')
        except Exception as e:
            messages.error(request, f'Erro ao cancelar venda: {e}')
        return redirect('vendas:detalhe', pk=venda.pk)
