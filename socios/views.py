# socios/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from core.models import Socio, Dependente, CategoriaSocio 
from .forms import SocioForm, DependenteFormSet

class SocioListView(LoginRequiredMixin, ListView):
    model = Socio
    template_name = 'socios/socio_list.html'
    context_object_name = 'socios'
    paginate_by = 10

    def get_queryset(self):
        # ... (a lógica de get_queryset com os filtros continua a mesma) ...
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        categoria_id = self.request.GET.get('categoria')
        status = self.request.GET.get('status')
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(cpf__icontains=search_query) |
                Q(num_registro__icontains=search_query)
            )
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if status:
            queryset = queryset.filter(situacao=status)
        return queryset.annotate(num_dependentes=Count('dependentes')).order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ... (código dos cards do dashboard) ...
        todos_socios = Socio.objects.all()
        context['total_socios'] = todos_socios.count()
        context['socios_ativos'] = todos_socios.filter(situacao='ATIVO').count()
        context['total_dependentes'] = Dependente.objects.count()
        context['total_titulares'] = context['total_socios']
        
        # --- ENVIANDO DADOS DOS FILTROS PARA O TEMPLATE (COM CORREÇÃO) ---
        context['categorias'] = CategoriaSocio.objects.all()
        # AQUI ESTÁ A CORREÇÃO: Passamos as choices do modelo diretamente
        context['situacao_choices'] = Socio.Situacao.choices 
        
        context['search_query'] = self.request.GET.get('q', '')
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['status_selecionado'] = self.request.GET.get('status', '')
        
        # ... (lógica da foto_existe) ...
        for socio in context['socios']:
            socio.foto_existe = False
            if socio.foto and socio.foto.storage.exists(socio.foto.name):
                socio.foto_existe = True
        
        return context
            
class SocioCreateView(LoginRequiredMixin, CreateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socios/socio_form.html'
    # Após salvar com sucesso, redireciona para a lista de sócios
    success_url = reverse_lazy('socios:lista_socios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Adicionar Sócio'
        context['titulo_cabecalho'] = 'Adicionar Novo Sócio'
        return context

class SocioUpdateView(LoginRequiredMixin, UpdateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socios/socio_form.html'
    success_url = reverse_lazy('socios:lista_socios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Sócio'
        context['titulo_cabecalho'] = f'Editando: {self.object.nome}'
        if self.request.POST:
            context['dependente_formset'] = DependenteFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['dependente_formset'] = DependenteFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        dependente_formset = context['dependente_formset']
        if dependente_formset.is_valid():
            self.object = form.save()
            dependente_formset.instance = self.object
            dependente_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
        
            
class SocioDeleteView(LoginRequiredMixin, DeleteView):
    model = Socio
    template_name = 'socios/socio_confirm_delete.html' # Um novo template de confirmação
    success_url = reverse_lazy('socios:lista_socios')

