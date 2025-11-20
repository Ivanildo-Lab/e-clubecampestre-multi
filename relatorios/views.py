# relatorios/views.py

from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, DecimalField 
from django.db.models.functions import Coalesce 
from django.utils import timezone
from django.utils.formats import date_format
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import datetime

# Importações de Modelos e Formulários
from financeiro.models import Mensalidade, Conta, LancamentoCaixa
from .forms import FiltroInadimplenciaMensalForm, FiltroContasForm

class RelatorioInadimplenciaView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/inadimplencia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        hoje = timezone.now()
        mes_selecionado = int(self.request.GET.get('mes', hoje.month))
        ano_selecionado = int(self.request.GET.get('ano', hoje.year))
        
        form = FiltroInadimplenciaMensalForm(self.request.GET or None, initial={'mes': mes_selecionado, 'ano': ano_selecionado})
        context['form'] = form

        mensalidades_do_mes = Mensalidade.objects.filter(
            socio__empresa=empresa_atual,
            competencia__month=mes_selecionado,
            competencia__year=ano_selecionado,
            status__in=['PENDENTE', 'ATRASADA']
        ).select_related('socio').order_by('socio__nome')

        context['inadimplentes'] = mensalidades_do_mes
        context['total_geral_inadimplencia'] = mensalidades_do_mes.aggregate(total=Sum('valor'))['total'] or 0
        context['mes_selecionado_nome'] = date_format(datetime.date(2000, mes_selecionado, 1), "F").capitalize()
        context['ano_selecionado'] = ano_selecionado
        context['titulo_pagina'] = 'Relatório de Inadimplência Mensal'
        return context

class RelatorioInadimplenciaPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        empresa_atual = request.user.empresa
        hoje = timezone.now()
        
        try:
            mes_selecionado = int(request.GET.get('mes') or hoje.month)
            ano_selecionado = int(request.GET.get('ano') or hoje.year)
        except (ValueError, TypeError):
            mes_selecionado = hoje.month
            ano_selecionado = hoje.year

        inadimplentes = Mensalidade.objects.filter(
            socio__empresa=empresa_atual,
            competencia__month=mes_selecionado,
            competencia__year=ano_selecionado,
            status__in=['PENDENTE', 'ATRASADA']
        ).select_related('socio').order_by('socio__nome')

        total_geral = inadimplentes.aggregate(total=Sum('valor'))['total'] or 0
        mes_nome = date_format(datetime.date(2000, mes_selecionado, 1), "F").capitalize()

        context = {
            'inadimplentes': inadimplentes,
            'empresa': empresa_atual,
            'mes_referencia': f"{mes_nome} de {ano_selecionado}",
            'total_geral': total_geral,
            'data_emissao': timezone.now()
        }

        html_string = render_to_string('relatorios/inadimplencia_pdf_template.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="relatorio_inadimplencia_{mes_selecionado}_{ano_selecionado}.pdf"'
        
        return response

class RelatorioContasView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/contas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        form = FiltroContasForm(self.request.GET or None)
        context['form'] = form
        contas = Conta.objects.filter(empresa=empresa_atual).select_related('plano_de_contas')
        if form.is_valid():
            data_inicio = form.cleaned_data.get('data_inicio')
            data_fim = form.cleaned_data.get('data_fim')
            tipo = form.cleaned_data.get('tipo')
            status = form.cleaned_data.get('status')
            if data_inicio:
                contas = contas.filter(data_vencimento__gte=data_inicio)
            if data_fim:
                contas = contas.filter(data_vencimento__lte=data_fim)
            if tipo:
                contas = contas.filter(plano_de_contas__tipo=tipo)
            if status:
                contas = contas.filter(status=status)
        
        context['contas'] = contas.order_by('data_vencimento')
        context['titulo_pagina'] = 'Relatório de Contas a Pagar/Receber'
        return context

class RelatorioDREView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/dre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        hoje = timezone.now()
        data_inicio_str = self.request.GET.get('data_inicio', hoje.replace(day=1).strftime('%Y-%m-%d'))
        data_fim_str = self.request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))
        
        lancamentos = LancamentoCaixa.objects.filter(
            empresa=empresa_atual,
            data_lancamento__gte=data_inicio_str,
            data_lancamento__lte=data_fim_str
        )

        # A CORREÇÃO ESTÁ AQUI: Calculamos os totais de forma segura primeiro
        total_receitas = lancamentos.filter(valor__gt=0).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']
        total_despesas = lancamentos.filter(valor__lt=0).aggregate(
            total=Coalesce(Sum('valor'), 0, output_field=DecimalField())
        )['total']

        # E depois agrupamos para a exibição detalhada
        receitas_agrupadas = lancamentos.filter(valor__gt=0).values('plano_de_contas__nome').annotate(total=Sum('valor')).order_by('-total')
        despesas_agrupadas = lancamentos.filter(valor__lt=0).values('plano_de_contas__nome').annotate(total=Sum('valor')).order_by('total')
        
        context['receitas'] = receitas_agrupadas
        context['despesas'] = despesas_agrupadas
        context['total_receitas'] = total_receitas
        context['total_despesas'] = abs(total_despesas) 
        context['saldo_periodo'] = total_receitas + total_despesas # O cálculo do saldo usa o valor negativo original
        
        context['data_inicio'] = data_inicio_str
        context['data_fim'] = data_fim_str
        context['titulo_pagina'] = 'Demonstrativo de Resultados'
        despesas_processadas = []
        for d in despesas_agrupadas:
            despesas_processadas.append({
                'plano_de_contas__nome': d['plano_de_contas__nome'],
                'total': abs(d['total'])
            })
        
        context['receitas'] = receitas_agrupadas
        context['despesas'] = despesas_processadas # <-- Usa a lista processada
        context['total_receitas'] = total_receitas
        context['total_despesas'] = abs(total_despesas)
        context['saldo_periodo'] = total_receitas + total_despesas

        return context

# Adicione esta nova view no final de relatorios/views.py

class RelatorioContasPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        empresa_atual = request.user.empresa
        
        # Usa o mesmo formulário e lógica de filtro da view principal
        form = FiltroContasForm(request.GET or None)
        contas = Conta.objects.filter(empresa=empresa_atual).select_related('plano_de_contas')

        if form.is_valid():
            data_inicio = form.cleaned_data.get('data_inicio')
            data_fim = form.cleaned_data.get('data_fim')
            tipo = form.cleaned_data.get('tipo')
            if data_inicio:
                contas = contas.filter(data_vencimento__gte=data_inicio)
            if data_fim:
                contas = contas.filter(data_vencimento__lte=data_fim)
            if tipo:
                contas = contas.filter(plano_de_contas__tipo=tipo)

        # Prepara o contexto para o template do PDF
        context = {
            'contas': contas.order_by('data_vencimento'),
            'empresa': empresa_atual,
            'filtros': request.GET, # Passa os filtros para exibição no relatório
            'data_emissao': timezone.now()
        }
        
        # Renderiza e gera o PDF
        html_string = render_to_string('relatorios/contas_pdf_template.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="relatorio_contas.pdf"'
        return response