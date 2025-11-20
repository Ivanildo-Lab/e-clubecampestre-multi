# core/views.py

import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.urls import reverse_lazy

from .models import Empresa, Socio, Dependente
from financeiro.models import Mensalidade
from .help_data import PARAMETROS_SISTEMA # Importa nossa lista de ajuda


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = reverse_lazy('usuarios:site-login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Dashboard'
        
        # A MUDANÇA MAIS IMPORTANTE: Pega a empresa do usuário logado
        empresa_atual = self.request.user.empresa
        
        # Se por algum motivo o usuário não tiver empresa (ex: superuser), não quebra
        if not empresa_atual:
            return context

        Mensalidade.objects.atualizar_status_atrasadas()
        hoje = timezone.now()

        # --- DADOS PARA OS CARDS (AGORA FILTRADOS PELA EMPRESA) ---
        socios_da_empresa = Socio.objects.filter(empresa=empresa_atual)
        mensalidades_da_empresa = Mensalidade.objects.filter(socio__empresa=empresa_atual)

        context['total_socios'] = socios_da_empresa.filter(situacao='ATIVO').count()
        
        mensalidades_mes_corrente = mensalidades_da_empresa.filter(competencia__month=hoje.month, competencia__year=hoje.year)
        context['receita_mensal'] = mensalidades_mes_corrente.filter(status='PAGA').aggregate(total=Sum('valor'))['total'] or 0
        
        pendentes_e_atrasadas = mensalidades_da_empresa.filter(status__in=['PENDENTE', 'ATRASADA'])
        context['pagamentos_pendentes'] = pendentes_e_atrasadas.count()

        total_cobradas_geral = mensalidades_da_empresa.count()
        if total_cobradas_geral > 0:
            taxa_inadimplencia = (pendentes_e_atrasadas.filter(status='ATRASADA').count() / total_cobradas_geral) * 100
        else:
            taxa_inadimplencia = 0
        context['taxa_inadimplencia'] = round(taxa_inadimplencia, 2)

        # --- DADOS PARA O GRÁFICO (AGORA FILTRADOS PELA EMPRESA) ---
        seis_meses_atras = hoje - timezone.timedelta(days=180)
        receitas_por_mes = mensalidades_da_empresa.filter(
            status='PAGA',
            data_pagamento__gte=seis_meses_atras
        ).annotate(
            mes=TruncMonth('data_pagamento')
        ).values('mes').annotate(
            total=Sum('valor')
        ).order_by('mes')

        chart_labels = [mes['mes'].strftime('%b/%Y') for mes in receitas_por_mes]
        chart_data = [float(mes['total']) for mes in receitas_por_mes]
        context['chart_labels_json'] = json.dumps(chart_labels)
        context['chart_data_json'] = json.dumps(chart_data)

        # --- DADOS PARA ATIVIDADE RECENTE (AGORA FILTRADOS PELA EMPRESA) ---
        context['atividades_recentes'] = mensalidades_da_empresa.filter(status='PAGA').order_by('-data_pagamento')[:5]

        # --- DADOS PARA LISTA DE INADIMPLENTES (AGORA FILTRADOS PELA EMPRESA) ---
        context['inadimplentes'] = pendentes_e_atrasadas.filter(
            status='ATRASADA'
        ).select_related('socio').order_by('data_vencimento')[:10]
        
        return context

class LandingPageView(TemplateView):
    template_name = 'landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        empresa_para_exibir = None
        
        # A única lógica: se o usuário estiver logado e tiver uma empresa,
        # nós a definimos. Caso contrário, a variável permanece 'None'.
        if self.request.user.is_authenticated and hasattr(self.request.user, 'empresa'):
            empresa_para_exibir = self.request.user.empresa
            
        context['empresa_logada'] = empresa_para_exibir
        return context

# No final de core/views.py
from .help_data import PARAMETROS_SISTEMA # Importa nossa lista de ajuda

class HelpView(LoginRequiredMixin, TemplateView):
    template_name = 'core/ajuda.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Ajuda e Parâmetros do Sistema'
        context['parametros'] = PARAMETROS_SISTEMA
        return context
