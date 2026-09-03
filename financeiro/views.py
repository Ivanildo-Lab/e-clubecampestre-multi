# financeiro/views.py

from django.views.generic import ListView, View, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.db import transaction
from decimal import Decimal

# Importações de Modelos e Formulários
from .models import Mensalidade, LancamentoCaixa, Caixa, PlanoDeContas, Conta
from .forms import MensalidadeForm, PlanoDeContasForm, CaixaForm, ContaForm,GerarMensalidadesForm,GerarMensalidadePorSocioForm,LancamentoCaixaForm, BaixaMensalidadeForm, BaixaContaForm
from core.models import CategoriaSocio, ConfiguracaoSistema, Convenio, Socio
from django.views.generic import FormView

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

class GerarMensalidadesEmMassaView(LoginRequiredMixin, FormView):
    template_name = 'financeiro/gerar_mensalidades_form.html'
    form_class = GerarMensalidadesForm
    success_url = reverse_lazy('financeiro:lista_mensalidades')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Geracao de Mensalidades - Passo 1'
        return context

    def _get_valor_vencimento(self, socio, origem, convenio_selecionado, categoria_selecionada):
        # Retorna (valor, dia) conforme origem e seleção
        valor = Decimal('0.00')
        dia = 10
        if origem == 'convenio':
            if convenio_selecionado:
                valor = convenio_selecionado.valor_mensalidade
                dia = convenio_selecionado.dia_vencimento or socio.categoria.dia_vencimento
                if valor <= 0 and socio.convenio and socio.convenio.valor_mensalidade > 0:
                    valor = socio.convenio.valor_mensalidade
                    dia = socio.convenio.dia_vencimento or dia
                if valor <= 0:
                    valor = socio.categoria.valor_mensalidade
                    dia = socio.categoria.dia_vencimento
            else:
                # Todos os convênios: prioriza convênio do sócio, senão categoria
                if socio.convenio and socio.convenio.valor_mensalidade > 0:
                    valor = socio.convenio.valor_mensalidade
                    dia = socio.convenio.dia_vencimento or socio.categoria.dia_vencimento
                else:
                    valor = socio.categoria.valor_mensalidade
                    dia = socio.categoria.dia_vencimento
        else:  # categoria
            if categoria_selecionada:
                valor = categoria_selecionada.valor_mensalidade
                dia = categoria_selecionada.dia_vencimento
            else:
                valor = socio.categoria.valor_mensalidade
                dia = socio.categoria.dia_vencimento
            # Fallback para convênio do sócio se categoria valor 0
            if valor <= 0 and socio.convenio and socio.convenio.valor_mensalidade > 0:
                valor = socio.convenio.valor_mensalidade
                dia = socio.convenio.dia_vencimento or dia
        if dia == 0:
            dia = socio.categoria.dia_vencimento or 10
        return valor, dia

    def form_valid(self, form):
        if not (self.request.user.is_superuser or self.request.user.nivel_acesso == 'ADMIN'):
            messages.error(self.request, 'Voce nao tem permissao para executar esta acao.')
            return redirect('financeiro:lista_mensalidades')

        empresa_atual = self.request.user.empresa
        origem = form.cleaned_data.get('origem')
        categoria = form.cleaned_data.get('categoria')
        convenio = form.cleaned_data.get('convenio')
        periodo = form.cleaned_data.get('periodo')
        meses_a_gerar = 1 if periodo == 'mes' else 12

        socios_ativos = Socio.objects.filter(
            empresa_id=empresa_atual.id,
            situacao=Socio.Situacao.ATIVO
        ).select_related('categoria', 'convenio')

        if origem == 'convenio' and convenio:
            socios_ativos = socios_ativos.filter(convenio_id=convenio.id)
        elif origem == 'categoria' and categoria:
            socios_ativos = socios_ativos.filter(categoria_id=categoria.id)

        import datetime
        hoje = datetime.date.today()
        socios_preview = []

        for socio in socios_ativos:
            valor, dia_vencimento = self._get_valor_vencimento(socio, origem, convenio, categoria)
            if valor is None or valor <= 0:
                continue
            competencia = hoje.replace(day=1)
            try:
                vencimento = competencia.replace(day=dia_vencimento)
            except ValueError:
                import calendar
                ultimo_dia = calendar.monthrange(competencia.year, competencia.month)[1]
                vencimento = competencia.replace(day=ultimo_dia)

            ja_existe = Mensalidade.objects.filter(
                socio=socio, competencia=competencia
            ).exists()

            if not ja_existe:
                # Exibe valor/dia usados - armazena como string/iso para sessão JSON-serializable
                convenio_nome = socio.convenio.nome if socio.convenio else "-"
                socios_preview.append({
                    'socio_id': socio.id,
                    'socio_nome': socio.nome,
                    'categoria': socio.categoria.nome,
                    'convenio': convenio_nome,
                    'valor': str(valor),
                    'competencia': competencia.isoformat(),
                    'vencimento': vencimento.isoformat(),
                })

        if not socios_preview:
            messages.info(self.request, 'Nenhuma nova mensalidade precisava ser gerada para os filtros selecionados.')
            return redirect('financeiro:lista_mensalidades')

        request.session['preview_geracao'] = {
            'origem': origem,
            'convenio_id': convenio.id if convenio else None,
            'categoria_id': categoria.id if categoria else None,
            'meses_a_gerar': meses_a_gerar,
            'socios': socios_preview,
        }

        return redirect('financeiro:preview_geracao_mensalidades')


class GerarMensalidadePorSocioView(LoginRequiredMixin, FormView):
    template_name = 'financeiro/gerar_mensalidade_socio_form.html'
    form_class = GerarMensalidadePorSocioForm
    success_url = reverse_lazy('financeiro:lista_mensalidades')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        socio_id = self.request.GET.get('socio') or self.kwargs.get('pk')
        if socio_id:
            initial['socio'] = socio_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Gerar Mensalidade por Sócio'
        return context

    def form_valid(self, form):
        if not (self.request.user.is_superuser or self.request.user.nivel_acesso == 'ADMIN'):
            messages.error(self.request, 'Voce nao tem permissao para executar esta acao.')
            return redirect('financeiro:lista_mensalidades')

        socio = form.cleaned_data['socio']
        periodo = form.cleaned_data['periodo']
        meses_a_gerar = 1 if periodo == 'mes' else 12

        # Valida pertence à empresa
        if socio.empresa_id != self.request.user.empresa.id:
            messages.error(self.request, 'Sócio não pertence à sua empresa.')
            return redirect('financeiro:gerar_mensalidade_socio')

        # Usa valor do convênio se existir e >0, senão categoria
        if socio.convenio and socio.convenio.valor_mensalidade > 0:
            valor = socio.convenio.valor_mensalidade
            dia_vencimento = socio.convenio.dia_vencimento or socio.categoria.dia_vencimento
        else:
            valor = socio.categoria.valor_mensalidade
            dia_vencimento = socio.categoria.dia_vencimento
        if dia_vencimento == 0:
            dia_vencimento = 10
        if valor is None or valor <= 0:
            messages.error(self.request, f'O sócio {socio.nome} está em categoria/convênio sem valor de mensalidade definido ({valor}). Ajuste no cadastro.')
            return redirect('financeiro:gerar_mensalidade_socio')

        import datetime, calendar
        hoje = datetime.date.today()
        socios_preview = []
        for i in range(meses_a_gerar):
            ano_comp = hoje.year + (hoje.month + i - 1) // 12
            mes_comp = (hoje.month + i - 1) % 12 + 1
            competencia = datetime.date(ano_comp, mes_comp, 1)
            if Mensalidade.objects.filter(socio=socio, competencia=competencia).exists():
                continue
            try:
                vencimento = competencia.replace(day=dia_vencimento)
            except ValueError:
                ultimo = calendar.monthrange(competencia.year, competencia.month)[1]
                vencimento = competencia.replace(day=ultimo)
            socios_preview.append({
                'socio_id': socio.id,
                'socio_nome': socio.nome,
                'categoria': socio.categoria.nome,
                'convenio': socio.convenio.nome if socio.convenio else '-',
                'valor': str(valor),
                'competencia': competencia.isoformat(),
                'vencimento': vencimento.isoformat(),
            })

        if not socios_preview:
            messages.info(self.request, f'Nenhuma nova mensalidade a gerar para {socio.nome} no período selecionado.')
            return redirect('financeiro:lista_mensalidades')

        # Reusa mesma sessão do fluxo em massa para aproveitar preview/confirm
        self.request.session['preview_geracao'] = {
            'origem': 'socio_unico',
            'convenio_id': socio.convenio.id if socio.convenio else None,
            'categoria_id': socio.categoria.id,
            'meses_a_gerar': meses_a_gerar,
            'socios': socios_preview,
        }
        return redirect('financeiro:preview_geracao_mensalidades')


class PreviewGerarMensalidadesView(LoginRequiredMixin, View):
    def get(self, request):
        if not (request.user.is_superuser or request.user.nivel_acesso == 'ADMIN'):
            messages.error(request, 'Voce nao tem permissao para executar esta acao.')
            return redirect('financeiro:lista_mensalidades')

        preview_data = request.session.get('preview_geracao')
        if not preview_data:
            messages.error(request, 'Dados de preview nao encontrados. Por favor, faca o processo novamente.')
            return redirect('financeiro:gerar_mensalidades_massa')

        # Converte valores de sessão (JSON-serializáveis) para tipos usáveis no template
        socios = []
        for item in preview_data.get('socios', []):
            # competencia/vencimento podem estar como isoformat string
            comp = item.get('competencia')
            venc = item.get('vencimento')
            try:
                if isinstance(comp, str):
                    comp = datetime.date.fromisoformat(comp)
            except:
                pass
            try:
                if isinstance(venc, str):
                    venc = datetime.date.fromisoformat(venc)
            except:
                pass
            # valor pode estar como string
            socios.append({
                'socio_id': item.get('socio_id'),
                'socio_nome': item.get('socio_nome'),
                'categoria': item.get('categoria'),
                'convenio': item.get('convenio'),
                'valor': item.get('valor'),
                'competencia': comp,
                'vencimento': venc,
            })

        context = {
            'titulo_pagina': 'Geracao de Mensalidades - Passo 2: Confirmar',
            'socios_preview': socios,
            'meses_a_gerar': preview_data['meses_a_gerar'],
            'origem': preview_data.get('origem', 'convenio'),
            'convenio_id': preview_data.get('convenio_id'),
            'categoria_id': preview_data.get('categoria_id'),
        }
        return render(request, 'financeiro/preview_gerar_mensalidades.html', context)


class ConfirmarGeracaoMensalidadesView(LoginRequiredMixin, View):
    def post(self, request):
        if not (request.user.is_superuser or request.user.nivel_acesso == 'ADMIN'):
            messages.error(request, 'Voce nao tem permissao para executar esta acao.')
            return redirect('financeiro:lista_mensalidades')

        empresa_atual = request.user.empresa
        meses_a_gerar = int(request.POST.get('meses_a_gerar', 1))
        convenio_id = request.POST.get('convenio_id')
        categoria_id = request.POST.get('categoria_id')
        origem = request.POST.get('origem', 'convenio')

        socios_ids = request.POST.getlist('socios_selecionados')
        valores = request.POST.getlist('valores')

        import datetime
        hoje = datetime.date.today()
        mensalidades_para_criar = []
        num_ignoradas = 0

        # Recupera objetos selecionados para recalcular dia se valor não editado
        convenio_sel = None
        categoria_sel = None
        if convenio_id:
            try:
                from core.models import Convenio
                convenio_sel = Convenio.objects.get(id=convenio_id, empresa=empresa_atual)
            except:
                pass
        if categoria_id:
            try:
                from core.models import CategoriaSocio
                categoria_sel = CategoriaSocio.objects.get(id=categoria_id, empresa=empresa_atual)
            except:
                pass

        for i in range(meses_a_gerar):
            ano_competencia = hoje.year + (hoje.month + i - 1) // 12
            mes_competencia = (hoje.month + i - 1) % 12 + 1
            competencia = hoje.replace(day=1).replace(year=ano_competencia, month=mes_competencia)

            socios_com_mensalidade = Mensalidade.objects.filter(
                socio__empresa_id=empresa_atual.id,
                competencia=competencia
            ).values_list('socio_id', flat=True)

            for idx, socio_id in enumerate(socios_ids):
                socio_id = int(socio_id)
                if socio_id in socios_com_mensalidade:
                    continue

                socio = Socio.objects.select_related('categoria', 'convenio').get(id=socio_id)
                # Valor vem do preview editável; dia vem da origem selecionada
                valor = Decimal(valores[idx]) if idx < len(valores) else Decimal('0')
                # Determina dia conforme origem
                if origem == 'convenio':
                    if convenio_sel and convenio_sel.dia_vencimento:
                        dia_vencimento = convenio_sel.dia_vencimento
                    elif socio.convenio and socio.convenio.dia_vencimento:
                        dia_vencimento = socio.convenio.dia_vencimento
                    else:
                        dia_vencimento = socio.categoria.dia_vencimento
                else:
                    if categoria_sel and categoria_sel.dia_vencimento:
                        dia_vencimento = categoria_sel.dia_vencimento
                    else:
                        dia_vencimento = socio.categoria.dia_vencimento
                if dia_vencimento == 0:
                    dia_vencimento = 10

                if valor <= 0:
                    num_ignoradas += 1
                    continue

                try:
                    vencimento = competencia.replace(day=dia_vencimento)
                except ValueError:
                    import calendar
                    ultimo_dia = calendar.monthrange(competencia.year, competencia.month)[1]
                    vencimento = competencia.replace(day=ultimo_dia)

                mensalidades_para_criar.append(Mensalidade(
                    socio=socio, competencia=competencia, valor=valor, data_vencimento=vencimento
                ))

        if mensalidades_para_criar:
            from django.db import transaction
            with transaction.atomic():
                Mensalidade.objects.bulk_create(mensalidades_para_criar)

        if 'preview_geracao' in request.session:
            del request.session['preview_geracao']

        num_criadas = len(mensalidades_para_criar)
        if num_criadas > 0:
            messages.success(request, f'{num_criadas} novas mensalidades foram geradas com sucesso.')
        else:
            messages.info(request, 'Nenhuma nova mensalidade foi gerada.')

        if num_ignoradas > 0:
            messages.warning(request, f'{num_ignoradas} socios foram ignorados (valor zero).')

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
        convenio_id = self.request.GET.get('convenio')

        if search_query:
            queryset = queryset.filter(socio__nome__icontains=search_query)
        if status:
            queryset = queryset.filter(status=status)
        if categoria_id:
            queryset = queryset.filter(socio__categoria_id=categoria_id)
        if convenio_id:
            queryset = queryset.filter(socio__convenio_id=convenio_id)
            
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
        context['convenios'] = Convenio.objects.filter(empresa=empresa_atual) # Adicionado para o filtro
        context['situacao_choices'] = Mensalidade.StatusChoice.choices
        
        context['search_query'] = self.request.GET.get('q', '')
        context['status_selecionado'] = self.request.GET.get('status', '')
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['convenio_selecionado'] = self.request.GET.get('convenio', '')
        context['baixa_form'] = BaixaMensalidadeForm(empresa=empresa_atual)
        return context


class BaixarMensalidadeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        empresa_atual = request.user.empresa
        mensalidade = get_object_or_404(Mensalidade, pk=pk, socio__empresa=empresa_atual)
        form = BaixaMensalidadeForm(request.POST, empresa=empresa_atual)

        if form.is_valid():
            caixa = form.cleaned_data.get('caixa')
            forma_pagamento = form.cleaned_data.get('forma_pagamento')
            data_pagamento = form.cleaned_data['data_pagamento']
            valor_juros = form.cleaned_data.get('valor_juros') or Decimal('0.00')

            try:
                with transaction.atomic():
                    mensalidade.status = 'PAGA'
                    mensalidade.data_pagamento = data_pagamento
                    mensalidade.forma_pagamento = forma_pagamento
                    mensalidade.save()

                    # PASSO 2: Lançar no caixa (SÓ SE UM CAIXA FOI SELECIONADO)
                    if caixa:
                        # Busca os planos de contas necessários
                        plano_contas_mensalidade_id = int(ConfiguracaoSistema.objects.get(empresa=empresa_atual, chave='PLANO_CONTAS_MENSALIDADE_ID').valor)
                        plano_contas_mensalidade = PlanoDeContas.objects.get(id=plano_contas_mensalidade_id)
                        
                        plano_contas_juros_id = int(ConfiguracaoSistema.objects.get(empresa=empresa_atual, chave='PLANO_CONTAS_JUROS_ID').valor)
                        plano_contas_juros = PlanoDeContas.objects.get(id=plano_contas_juros_id)

                        # Cria o Lançamento do valor principal
                        LancamentoCaixa.objects.create(
                            empresa=empresa_atual, caixa=caixa, plano_de_contas=plano_contas_mensalidade,
                            data_lancamento=data_pagamento, descricao=f"Pag. Mensalidade: {mensalidade.socio.nome} ({mensalidade.competencia.strftime('%m/%Y')})",
                            valor=mensalidade.valor, mensalidade_origem=mensalidade
                        )

                        # Se houver juros, cria um lançamento separado para eles
                        if valor_juros > 0:
                            LancamentoCaixa.objects.create(
                                empresa=empresa_atual, caixa=caixa, plano_de_contas=plano_contas_juros,
                                data_lancamento=data_pagamento, descricao=f"Juros Mens.: {mensalidade.socio.nome} ({mensalidade.competencia.strftime('%m/%Y')})",
                                valor=valor_juros, mensalidade_origem=mensalidade
                            )
                        
                        messages.success(request, f'Mensalidade de {mensalidade.socio.nome} baixada e lançada no caixa "{caixa.nome}" com sucesso!')
                    
                    else: # Se nenhum caixa foi selecionado
                        messages.success(request, f'Mensalidade de {mensalidade.socio.nome} baixada com sucesso (sem lançamento no caixa).')

            except (ConfiguracaoSistema.DoesNotExist, PlanoDeContas.DoesNotExist):
                messages.error(request, 'Erro de configuração! Verifique os Parâmetros do Sistema para o financeiro.')
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
        return PlanoDeContas.objects.filter(empresa=self.request.user.empresa).order_by('codigo')

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

class MensalidadePDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        empresa_atual = request.user.empresa
        queryset = Mensalidade.objects.filter(socio__empresa=empresa_atual)
        
        # Filtros
        search_query = request.GET.get('q')
        status = request.GET.get('status')
        categoria_id = request.GET.get('categoria')
        convenio_id = request.GET.get('convenio')
        
        # Filtros de data (se existirem na URL, assumindo que você pode querer filtrar por data no futuro)
        # Se não tiver filtro de data na tela de mensalidades ainda, isso prepara o terreno.
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if search_query: queryset = queryset.filter(socio__nome__icontains=search_query)
        if status: queryset = queryset.filter(status=status)
        if categoria_id: queryset = queryset.filter(socio__categoria_id=categoria_id)
        if convenio_id: queryset = queryset.filter(socio__convenio_id=convenio_id)
        
        # Logica para filtro de data (opcional, caso adicione no futuro)
        if data_inicio: queryset = queryset.filter(data_vencimento__gte=data_inicio)
        if data_fim: queryset = queryset.filter(data_vencimento__lte=data_fim)

        mensalidades = queryset.select_related('socio', 'socio__categoria').order_by('data_vencimento')
        total_geral = mensalidades.aggregate(total=Sum('valor'))['total'] or 0

        # --- BUSCANDO OS NOMES PARA O CABEÇALHO ---
        categoria_nome = None
        if categoria_id:
            cat = CategoriaSocio.objects.filter(id=categoria_id).first()
            if cat: categoria_nome = cat.nome

        convenio_nome = None
        if convenio_id:
            conv = Convenio.objects.filter(id=convenio_id).first()
            if conv: convenio_nome = conv.nome

        context = {
            'mensalidades': mensalidades,
            'empresa': empresa_atual,
            'total_geral': total_geral,
            'data_emissao': timezone.now(),
            # Dados para o cabeçalho dinâmico
            'filtro_categoria': categoria_nome,
            'filtro_convenio': convenio_nome,
            'filtro_status': status,
            'filtro_data_inicio': data_inicio,
            'filtro_data_fim': data_fim,
        }
        
        html_string = render_to_string('financeiro/mensalidade_pdf_template.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="relatorio_mensalidades.pdf"'
        return response

class FluxoDeCaixaPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        empresa_atual = request.user.empresa
        # Reaproveita exatamente a mesma lógica de filtro da FluxoDeCaixaView
        hoje_str = timezone.now().strftime('%Y-%m-%d')
        caixa_padrao_obj = ConfiguracaoSistema.objects.filter(empresa=empresa_atual, chave='CAIXA_PADRAO_ID').first()
        caixa_padrao_id = caixa_padrao_obj.valor if caixa_padrao_obj else None
        caixa_selecionado = request.GET.get('caixa', caixa_padrao_id)
        data_inicio = request.GET.get('data_inicio', hoje_str)
        data_fim = request.GET.get('data_fim', hoje_str)

        queryset = LancamentoCaixa.objects.filter(empresa=empresa_atual)
        if caixa_selecionado:
            queryset = queryset.filter(caixa_id=caixa_selecionado)
        if data_inicio:
            queryset = queryset.filter(data_lancamento__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_lancamento__lte=data_fim)

        lancamentos = queryset.select_related('caixa', 'plano_de_contas').order_by('data_lancamento', 'id')

        # Calculos idênticos ao FluxoDeCaixaView
        saldo_inicial = 0
        total_entradas = 0
        total_saidas_negativo = 0
        caixa_obj = None
        if caixa_selecionado:
            try:
                caixa_obj = Caixa.objects.get(id=caixa_selecionado, empresa=empresa_atual)
                saldo_inicial = caixa_obj.saldo_inicial
                lancamentos_anteriores_qs = LancamentoCaixa.objects.filter(caixa=caixa_obj)
                if data_inicio:
                    lancamentos_anteriores_qs = lancamentos_anteriores_qs.filter(data_lancamento__lt=data_inicio)
                lancamentos_anteriores = lancamentos_anteriores_qs.aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
                saldo_inicial += lancamentos_anteriores
                total_entradas = lancamentos.filter(valor__gt=0).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total'] or 0
                total_saidas_negativo = lancamentos.filter(valor__lt=0).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total'] or 0
            except Caixa.DoesNotExist:
                caixa_obj = None
                pass
        else:
            # Sem caixa selecionado, calcula totais do queryset geral
            total_entradas = lancamentos.filter(valor__gt=0).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total'] or 0
            total_saidas_negativo = lancamentos.filter(valor__lt=0).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total'] or 0

        saldo_final = saldo_inicial + total_entradas + total_saidas_negativo

        context = {
            'lancamentos': lancamentos,
            'empresa': empresa_atual,
            'caixa_obj': caixa_obj,
            'caixa_selecionado_id': caixa_selecionado,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'saldo_inicial': saldo_inicial,
            'total_entradas': total_entradas,
            'total_saidas_abs': abs(total_saidas_negativo),
            'saldo_final': saldo_final,
            'data_emissao': timezone.now(),
        }

        html_string = render_to_string('financeiro/fluxo_caixa_pdf_template.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="relatorio_fluxo_caixa.pdf"'
        return response