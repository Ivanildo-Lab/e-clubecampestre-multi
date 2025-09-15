# financeiro/views.py

from django.views.generic import ListView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.core.management import call_command

# Importações de Modelos e Formulários
from .models import Mensalidade
from .forms import MensalidadeForm
from core.models import CategoriaSocio

class GerarMensalidadesEmMassaView(LoginRequiredMixin, View):
    def post(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Você não tem permissão para executar esta ação.')
            return redirect('financeiro:lista_mensalidades')
        
        # TODO: Ajustar o comando 'gerar_mensalidades' para aceitar um parâmetro de empresa
        # e ser totalmente compatível com multi-tenancy.
        try:
            num_criadas, num_ignoradas = Mensalidade.objects.gerar_mensalidades_para_ativos()
            
            if num_criadas > 0:
                messages.success(request, f'{num_criadas} novas mensalidades foram geradas com sucesso.')
            else:
                messages.info(request, 'Nenhuma nova mensalidade precisava ser gerada. Todos os sócios ativos já estão em dia.')

            if num_ignoradas > 0:
                messages.warning(request, f'{num_ignoradas} sócios foram ignorados por não terem valor de mensalidade definido em sua categoria.')

        except Exception as e:
            messages.error(request, f'Ocorreu um erro inesperado: {e}')
            
        return redirect('financeiro:lista_mensalidades')

class MensalidadeListView(LoginRequiredMixin, ListView):
    model = Mensalidade
    template_name = 'financeiro/mensalidade_list.html'
    context_object_name = 'mensalidades'
    paginate_by = 15

    def get_queryset(self):
        Mensalidade.objects.atualizar_status_atrasadas()
        # Filtra mensalidades apenas da empresa do usuário logado
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
        context['titulo_pagina'] = 'Mensalidades'
        
        # Filtra categorias apenas da empresa do usuário logado
        context['categorias'] = CategoriaSocio.objects.filter(empresa=self.request.user.empresa)
        context['situacao_choices'] = Mensalidade.StatusChoice.choices
        context['search_query'] = self.request.GET.get('q', '')
        context['status_selecionado'] = self.request.GET.get('status', '')
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        return context

class MarcarComoPagaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Garante que a mensalidade pertence a um sócio da empresa do usuário
        mensalidade = get_object_or_404(Mensalidade, pk=pk, socio__empresa=request.user.empresa)
        
        if mensalidade.status != 'PAGA':
            mensalidade.status = 'PAGA'
            mensalidade.data_pagamento = timezone.now().date()
            mensalidade.save()
            messages.success(request, f"Mensalidade de {mensalidade.socio.nome} marcada como paga.")
        else:
            messages.info(request, "Esta mensalidade já estava paga.")
            
        return redirect('financeiro:lista_mensalidades')

class MensalidadeUpdateView(LoginRequiredMixin, UpdateView):
    model = Mensalidade
    form_class = MensalidadeForm
    template_name = 'financeiro/mensalidade_form.html'
    success_url = reverse_lazy('financeiro:lista_mensalidades')
    
    def get_queryset(self):
        # Garante que só se pode editar mensalidades da empresa do usuário
        return Mensalidade.objects.filter(socio__empresa=self.request.user.empresa)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Mensalidade'
        context['titulo_cabecalho'] = f'Editando Mensalidade de {self.object.socio.nome}'
        context['subtitulo_cabecalho'] = f'Competência: {self.object.competencia.strftime("%m/%Y")}'
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Você não tem permissão para editar mensalidades.')
            return redirect('financeiro:lista_mensalidades')
        return super().dispatch(request, *args, **kwargs)