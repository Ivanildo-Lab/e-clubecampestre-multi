# financeiro/views.py

from django.views.generic import ListView, View, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.db import transaction
from decimal import Decimal

# Importações de Modelos e Formulários
from .models import Mensalidade, LancamentoCaixa, Caixa, PlanoDeContas, Conta
from .forms import MensalidadeForm, PlanoDeContasForm, CaixaForm, ContaForm, LancamentoCaixaForm, BaixaMensalidadeForm, BaixaContaForm
from core.models import CategoriaSocio, ConfiguracaoSistema

class GerarMensalidadesEmMassaView(LoginRequiredMixin, View):
    def post(self, request):
        if not (request.user.is_superuser or request.user.nivel_acesso == 'ADMIN'):
            messages.error(request, 'Você não tem permissão para executar esta ação.')
            return redirect('financeiro:lista_mensalidades')
        
        empresa_atual = request.user.empresa
        if not empresa_atual:
            messages.error(request, 'Seu usuário não está associado a uma empresa.')
            return redirect('financeiro:lista_mensalidades')
        try:
            num_criadas, num_ignoradas = Mensalidade.objects.gerar_mensalidades_para_ativos(empresa_id=empresa_atual.id)
            if num_criadas > 0:
                messages.success(request, f'{num_criadas} novas mensalidades foram geradas com sucesso.')
            else:
                messages.info(request, 'Nenhuma nova mensalidade precisava ser gerada.')
            if num_ignoradas > 0:
                messages.warning(request, f'{num_ignoradas} sócios foram ignorados.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro: {e}')
        return redirect('financeiro:lista_mensalidades')

class MensalidadeListView(LoginRequiredMixin, ListView):
    model = Mensalidade
    template_name = 'financeiro/mensalidade_list.html'
    context_object_name = 'mensalidades'
    paginate_by = 15

    def get_queryset(self):
        Mensalidade.objects.atualizar_status_atrasadas()
        queryset = Mensalidade.objects.filter(socio__empresa=self.request.user.empresa)
        search_query = self.request.GET.get('q')
        status = self.request.GET.get('status')
        categoria_id = self.request.GET.get('categoria')
        if search_query:
            queryset = queryset.filter(socio__nome__icontains=search_query)
        if status:
            queryset = queryset.filter(status=status)
        if categoria_id:
            queryset = queryset.filter(socio__categoria_id=categoria_id)
        return queryset.select_related('socio', 'socio__categoria').order_by('-data_vencimento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        context['titulo_pagina'] = 'Mensalidades'
        context['caixas_disponiveis'] = Caixa.objects.filter(empresa=empresa_atual)
        caixa_padrao_obj = ConfiguracaoSistema.objects.filter(empresa=empresa_atual, chave='CAIXA_PADRAO_ID').first()
        context['caixa_padrao_id'] = int(caixa_padrao_obj.valor) if caixa_padrao_obj else None
        taxa_juros_obj = ConfiguracaoSistema.objects.filter(empresa=empresa_atual, chave='TAXA_JUROS_MENSAL').first()
        context['taxa_juros'] = taxa_juros_obj.valor if taxa_juros_obj else '0.0'
        context['categorias'] = CategoriaSocio.objects.filter(empresa=empresa_atual)
        context['situacao_choices'] = Mensalidade.StatusChoice.choices
        context['search_query'] = self.request.GET.get('q', '')
        context['status_selecionado'] = self.request.GET.get('status', '')
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        return context

class BaixarMensalidadeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        empresa_atual = request.user.empresa
        mensalidade = get_object_or_404(Mensalidade, pk=pk, socio__empresa=empresa_atual)
        form = BaixaMensalidadeForm(request.POST, empresa=empresa_atual)

        if form.is_valid():
            caixa = form.cleaned_data['caixa']
            data_pagamento = form.cleaned_data['data_pagamento']
            valor_juros = form.cleaned_data.get('valor_juros') or Decimal('0.00')

            try:
                plano_contas_mensalidade_id = int(ConfiguracaoSistema.objects.get(empresa=empresa_atual, chave='PLANO_CONTAS_MENSALIDADE_ID').valor)
                plano_contas_mensalidade = PlanoDeContas.objects.get(id=plano_contas_mensalidade_id)
                plano_contas_juros_id = int(ConfiguracaoSistema.objects.get(empresa=empresa_atual, chave='PLANO_CONTAS_JUROS_ID').valor)
                plano_contas_juros = PlanoDeContas.objects.get(id=plano_contas_juros_id)

                with transaction.atomic():
                    mensalidade.status = 'PAGA'
                    mensalidade.data_pagamento = data_pagamento
                    mensalidade.save()

                    LancamentoCaixa.objects.create(
                        empresa=empresa_atual, caixa=caixa, plano_de_contas=plano_contas_mensalidade,
                        data_lancamento=data_pagamento, descricao=f"Pag. Mensalidade: {mensalidade.socio.nome} ({mensalidade.competencia.strftime('%m/%Y')})",
                        valor=mensalidade.valor, mensalidade_origem=mensalidade
                    )

                    if valor_juros > 0:
                        LancamentoCaixa.objects.create(
                            empresa=empresa_atual, caixa=caixa, plano_de_contas=plano_contas_juros,
                            data_lancamento=data_pagamento, descricao=f"Juros Mens.: {mensalidade.socio.nome} ({mensalidade.competencia.strftime('%m/%Y')})",
                            valor=valor_juros,
                            mensalidade_origem=mensalidade
                        )
                
                messages.success(request, f'Mensalidade de {mensalidade.socio.nome} baixada com sucesso!')
            except (ConfiguracaoSistema.DoesNotExist, PlanoDeContas.DoesNotExist):
                messages.error(request, 'Erro de configuração! Verifique os parâmetros de Plano de Contas para Mensalidades e Juros.')
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao baixar a mensalidade: {e}")
        else:
            messages.error(request, f"Dados inválidos. Por favor, verifique: {form.errors}")
        
        return redirect('financeiro:lista_mensalidades')

class MensalidadeUpdateView(LoginRequiredMixin, UpdateView):
    model = Mensalidade
    form_class = MensalidadeForm
    template_name = 'financeiro/mensalidade_form.html'
    success_url = reverse_lazy('financeiro:lista_mensalidades')
    
    def get_queryset(self):
        return Mensalidade.objects.filter(socio__empresa=self.request.user.empresa)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Mensalidade'
        context['titulo_cabecalho'] = f'Editando Mensalidade de {self.object.socio.nome}'
        context['subtitulo_cabecalho'] = f'Competência: {self.object.competencia.strftime("%m/%Y")}'
        return context

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.nivel_acesso == 'ADMIN'):
            messages.error(request, 'Você não tem permissão para editar mensalidades.')
            return redirect('financeiro:lista_mensalidades')
        return super().dispatch(request, *args, **kwargs)

class MensalidadeDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mensalidade = get_object_or_404(Mensalidade, pk=pk, socio__empresa=request.user.empresa)
        if mensalidade.status == 'PAGA':
            messages.error(request, 'Não é possível excluir uma mensalidade que já foi paga.')
            return redirect('financeiro:lista_mensalidades')
        try:
            mensalidade.delete()
            messages.success(request, f'A mensalidade de {mensalidade.socio.nome} ({mensalidade.competencia.strftime("%m/%Y")}) foi excluída com sucesso.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao tentar excluir a mensalidade: {e}')
        return redirect('financeiro:lista_mensalidades')

class PlanoDeContasListView(LoginRequiredMixin, ListView):
    model = PlanoDeContas
    template_name = 'financeiro/plano_de_contas_list.html'
    context_object_name = 'planos_de_contas'
    def get_queryset(self):
        return PlanoDeContas.objects.filter(empresa=self.request.user.empresa).order_by('nome')

class PlanoDeContasCreateView(LoginRequiredMixin, CreateView):
    model = PlanoDeContas
    form_class = PlanoDeContasForm
    template_name = 'financeiro/plano_de_contas_form.html'
    success_url = reverse_lazy('financeiro:lista_plano_de_contas')
    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        messages.success(self.request, 'Conta adicionada ao plano com sucesso!')
        return super().form_valid(form)

class PlanoDeContasUpdateView(LoginRequiredMixin, UpdateView):
    model = PlanoDeContas
    form_class = PlanoDeContasForm
    template_name = 'financeiro/plano_de_contas_form.html'
    success_url = reverse_lazy('financeiro:lista_plano_de_contas')
    def get_queryset(self):
        return PlanoDeContas.objects.filter(empresa=self.request.user.empresa)
    def form_valid(self, form):
        messages.success(self.request, 'Conta atualizada com sucesso!')
        return super().form_valid(form)

class PlanoDeContasDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        conta = get_object_or_404(PlanoDeContas, pk=pk, empresa=request.user.empresa)
        try:
            nome_conta = conta.nome
            conta.delete()
            messages.success(request, f'A conta "{nome_conta}" foi excluída com sucesso.')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir a conta "{conta.nome}", pois ela pode estar em uso.')
        return redirect('financeiro:lista_plano_de_contas')

class CaixaListView(LoginRequiredMixin, ListView):
    model = Caixa
    template_name = 'financeiro/caixa_list.html'
    context_object_name = 'caixas'
    def get_queryset(self):
        return Caixa.objects.filter(empresa=self.request.user.empresa).order_by('nome')

class CaixaCreateView(LoginRequiredMixin, CreateView):
    model = Caixa
    form_class = CaixaForm
    template_name = 'financeiro/caixa_form.html'
    success_url = reverse_lazy('financeiro:lista_caixas')
    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        messages.success(self.request, 'Caixa/Conta adicionado com sucesso!')
        return super().form_valid(form)

class CaixaUpdateView(LoginRequiredMixin, UpdateView):
    model = Caixa
    form_class = CaixaForm
    template_name = 'financeiro/caixa_form.html'
    success_url = reverse_lazy('financeiro:lista_caixas')
    def get_queryset(self):
        return Caixa.objects.filter(empresa=self.request.user.empresa)
    def form_valid(self, form):
        messages.success(self.request, 'Caixa/Conta atualizado com sucesso!')
        return super().form_valid(form)

class CaixaDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        caixa = get_object_or_404(Caixa, pk=pk, empresa=request.user.empresa)
        try:
            nome_caixa = caixa.nome
            caixa.delete()
            messages.success(request, f'O caixa "{nome_caixa}" foi excluído com sucesso.')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir o caixa "{caixa.nome}", pois ele pode ter lançamentos associados.')
        return redirect('financeiro:lista_caixas')

class FluxoDeCaixaView(LoginRequiredMixin, ListView):
    model = LancamentoCaixa
    template_name = 'financeiro/fluxo_de_caixa.html'
    context_object_name = 'lancamentos'
    paginate_by = 30
    def get_queryset(self):
        empresa_atual = self.request.user.empresa
        queryset = LancamentoCaixa.objects.filter(empresa=empresa_atual)
        hoje_str = timezone.now().strftime('%Y-%m-%d')
        caixa_padrao_obj = ConfiguracaoSistema.objects.filter(empresa=empresa_atual, chave='CAIXA_PADRAO_ID').first()
        caixa_padrao_id = caixa_padrao_obj.valor if caixa_padrao_obj else None
        self.caixa_selecionado = self.request.GET.get('caixa', caixa_padrao_id)
        self.data_inicio = self.request.GET.get('data_inicio', hoje_str)
        self.data_fim = self.request.GET.get('data_fim', hoje_str)
        if self.caixa_selecionado:
            queryset = queryset.filter(caixa_id=self.caixa_selecionado)
        if self.data_inicio:
            queryset = queryset.filter(data_lancamento__gte=self.data_inicio)
        if self.data_fim:
            queryset = queryset.filter(data_lancamento__lte=self.data_fim)
        return queryset.select_related('caixa', 'plano_de_contas').order_by('-data_lancamento', '-id')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        context['titulo_pagina'] = 'Fluxo de Caixa'
        context['caixas'] = Caixa.objects.filter(empresa=empresa_atual)
        context['caixa_selecionado_id'] = self.caixa_selecionado
        context['data_inicio'] = self.data_inicio
        context['data_fim'] = self.data_fim
        saldo_inicial = 0
        total_entradas = 0
        total_saidas_negativo = 0
        if self.caixa_selecionado:
            try:
                caixa = Caixa.objects.get(id=self.caixa_selecionado, empresa=empresa_atual)
                saldo_inicial = caixa.saldo_inicial
                lancamentos_anteriores_qs = LancamentoCaixa.objects.filter(caixa=caixa)
                if self.data_inicio:
                    lancamentos_anteriores_qs = lancamentos_anteriores_qs.filter(data_lancamento__lt=self.data_inicio)
                lancamentos_anteriores = lancamentos_anteriores_qs.aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
                saldo_inicial += lancamentos_anteriores
                lancamentos_periodo = self.get_queryset()
                total_entradas = lancamentos_periodo.filter(valor__gt=0).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
                total_saidas_negativo = lancamentos_periodo.filter(valor__lt=0).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
            except Caixa.DoesNotExist:
                messages.error(self.request, "O caixa selecionado não foi encontrado.")
                pass
        context['saldo_inicial'] = saldo_inicial
        context['total_entradas'] = total_entradas
        context['total_saidas_abs'] = abs(total_saidas_negativo)
        context['saldo_final'] = saldo_inicial + total_entradas + total_saidas_negativo
        return context

class ContaListView(LoginRequiredMixin, ListView):
    model = Conta
    template_name = 'financeiro/conta_list.html'
    context_object_name = 'contas'
    paginate_by = 15
    def get_queryset(self):
        return Conta.objects.filter(empresa=self.request.user.empresa).order_by('-data_vencimento')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        context['caixas_disponiveis'] = Caixa.objects.filter(empresa=empresa_atual)
        caixa_padrao_obj = ConfiguracaoSistema.objects.filter(empresa=empresa_atual, chave='CAIXA_PADRAO_ID').first()
        if caixa_padrao_obj:
            context['caixa_padrao_id'] = int(caixa_padrao_obj.valor)
        else:
            context['caixa_padrao_id'] = None
        return context

class ContaCreateView(LoginRequiredMixin, CreateView):
    model = Conta
    form_class = ContaForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:lista_contas')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs
    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        messages.success(self.request, 'Conta adicionada com sucesso!')
        return super().form_valid(form)

class ContaUpdateView(LoginRequiredMixin, UpdateView):
    model = Conta
    form_class = ContaForm
    template_name = 'financeiro/conta_form.html'
    success_url = reverse_lazy('financeiro:lista_contas')
    def get_queryset(self):
        return Conta.objects.filter(empresa=self.request.user.empresa)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs
    def form_valid(self, form):
        messages.success(self.request, 'Conta atualizada com sucesso!')
        return super().form_valid(form)

class ContaDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        conta = get_object_or_404(Conta, pk=pk, empresa=request.user.empresa)
        if conta.status == 'PAGA':
            messages.error(request, 'Não é possível excluir uma conta que já foi paga.')
        else:
            nome_conta = conta.descricao
            conta.delete()
            messages.success(request, f'A conta "{nome_conta}" foi excluída com sucesso.')
        return redirect('financeiro:lista_contas')

class BaixarContaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        conta = get_object_or_404(Conta, pk=pk, empresa=request.user.empresa)
        form = BaixaContaForm(request.POST, empresa=request.user.empresa)
        if form.is_valid():
            caixa = form.cleaned_data['caixa']
            data_pagamento = form.cleaned_data['data_pagamento']
            try:
                with transaction.atomic():
                    conta.status = 'PAGA'
                    conta.data_pagamento = data_pagamento
                    conta.save()
                    valor_lancamento = conta.valor if conta.plano_de_contas.tipo == 'RECEITA' else -abs(conta.valor)
                    LancamentoCaixa.objects.create(
                        empresa=request.user.empresa,
                        caixa=caixa,
                        plano_de_contas=conta.plano_de_contas,
                        data_lancamento=data_pagamento,
                        descricao=f"Baixa da conta: {conta.descricao}",
                        valor=valor_lancamento,
                        conta_origem=conta
                    )
                messages.success(request, f'Conta "{conta.descricao}" baixada com sucesso!')
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao baixar a conta: {e}")
        else:
            messages.error(request, "Dados inválidos. Por favor, verifique.")
        return redirect('financeiro:lista_contas')

class LancamentoCaixaCreateView(LoginRequiredMixin, CreateView):
    model = LancamentoCaixa
    form_class = LancamentoCaixaForm
    template_name = 'financeiro/lancamento_caixa_form.html'
    success_url = reverse_lazy('financeiro:fluxo_de_caixa')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs
    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        messages.success(self.request, 'Lançamento manual adicionado ao caixa com sucesso!')
        return super().form_valid(form)

class LancamentoCaixaUpdateView(LoginRequiredMixin, UpdateView):
    model = LancamentoCaixa
    form_class = LancamentoCaixaForm
    template_name = 'financeiro/lancamento_caixa_form.html'
    success_url = reverse_lazy('financeiro:fluxo_de_caixa')
    def get_queryset(self):
        return LancamentoCaixa.objects.filter(empresa=self.request.user.empresa)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs
    def form_valid(self, form):
        messages.success(self.request, 'Lançamento atualizado com sucesso!')
        return super().form_valid(form)

class LancamentoCaixaDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lancamento = get_object_or_404(LancamentoCaixa, pk=pk, empresa=request.user.empresa)
        if lancamento.mensalidade_origem or lancamento.conta_origem:
            messages.error(request, 'Não é possível excluir um lançamento gerado automaticamente por uma baixa.')
        else:
            lancamento.delete()
            messages.success(request, 'O lançamento manual foi excluído com sucesso.')
        return redirect('financeiro:fluxo_de_caixa')
    