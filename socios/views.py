# socios/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
import datetime

# Importações de Modelos e Formulários
from core.models import Socio, Dependente, CategoriaSocio, Convenio
from financeiro.models import Mensalidade
from .forms import SocioForm, DependenteFormSet, CategoriaSocioForm, ConvenioForm

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

# --- Views de Sócio ---

class SocioListView(LoginRequiredMixin, ListView):
    model = Socio
    template_name = 'socios/socio_list.html'
    context_object_name = 'socios'
    paginate_by = 10

    def get_queryset(self):
        queryset = Socio.objects.filter(empresa=self.request.user.empresa)
        
        search_query = self.request.GET.get('q')
        categoria_id = self.request.GET.get('categoria')
        status = self.request.GET.get('status')
        if search_query:
            queryset = queryset.filter(Q(nome__icontains=search_query) | Q(cpf__icontains=search_query) | Q(num_registro__icontains=search_query))
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if status:
            queryset = queryset.filter(situacao=status)
        return queryset.annotate(num_dependentes=Count('dependentes')).order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_atual = self.request.user.empresa
        todos_socios = Socio.objects.filter(empresa=empresa_atual)
        context['total_socios'] = todos_socios.count()
        context['socios_ativos'] = todos_socios.filter(situacao='ATIVO').count()
        context['total_dependentes'] = Dependente.objects.filter(socio_titular__in=todos_socios).count()
        context['total_titulares'] = context['total_socios']
        context['categorias'] = CategoriaSocio.objects.filter(empresa=empresa_atual)
        context['situacao_choices'] = Socio.Situacao.choices
        context['search_query'] = self.request.GET.get('q', '')
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['status_selecionado'] = self.request.GET.get('status', '')
        for socio in context['socios']:
            socio.foto_existe = False
            if socio.foto and socio.foto.storage.exists(socio.foto.name):
                socio.foto_existe = True
        return context

class SocioCreateView(LoginRequiredMixin, CreateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socios/socio_form.html'
    success_url = reverse_lazy('socios:lista_socios')

    def get_form(self, form_class=None):
        """
        Este é o método correto para manipular o formulário.
        Ele é chamado antes de o formulário ser renderizado.
        """
        form = super().get_form(form_class)
        # Filtramos os campos de Categoria e Convênio pela empresa do usuário
        empresa_atual = self.request.user.empresa
        form.fields['categoria'].queryset = CategoriaSocio.objects.filter(empresa=empresa_atual)
        form.fields['convenio'].queryset = Convenio.objects.filter(empresa=empresa_atual)
        return form

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Adicionar Sócio'
        if self.request.POST:
            context['dependente_formset'] = DependenteFormSet(self.request.POST, self.request.FILES)
        else:
            context['dependente_formset'] = DependenteFormSet()
        return context


class SocioUpdateView(LoginRequiredMixin, UpdateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socios/socio_form.html'
    success_url = reverse_lazy('socios:lista_socios')
    
    def get_form(self, form_class=None):
        """
        Este é o único lugar que filtra os campos.
        """
        form = super().get_form(form_class)
        empresa_atual = self.request.user.empresa
        form.fields['categoria'].queryset = CategoriaSocio.objects.filter(empresa=empresa_atual)
        form.fields['convenio'].queryset = Convenio.objects.filter(empresa=empresa_atual)
        return form

    def get_queryset(self):
        return Socio.objects.filter(empresa=self.request.user.empresa)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Sócio'
        if self.request.POST:
            context['dependente_formset'] = DependenteFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['dependente_formset'] = DependenteFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        dependente_formset = context['dependente_formset']
        if form.is_valid() and dependente_formset.is_valid():
            self.object = form.save()
            dependente_formset.instance = self.object
            dependente_formset.save()
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))
    

class SocioDeleteView(LoginRequiredMixin, DeleteView):
    model = Socio
    template_name = 'socios/socio_confirm_delete.html'
    success_url = reverse_lazy('socios:lista_socios')

    def get_queryset(self):
        return Socio.objects.filter(empresa=self.request.user.empresa)

# Em socios/views.py

class GerarMensalidadeIndividualView(LoginRequiredMixin, View):
    def post(self, request, pk):
        socio = get_object_or_404(Socio, pk=pk, empresa=request.user.empresa)
        hoje = datetime.date.today()
        
        novas_mensalidades_criadas = []
        meses_a_gerar = 12

        # Loop pelos próximos 12 meses
        for i in range(meses_a_gerar):
            ano_competencia = hoje.year + (hoje.month + i - 1) // 12
            mes_competencia = (hoje.month + i - 1) % 12 + 1
            competencia = datetime.date(ano_competencia, mes_competencia, 1)

            # Verifica se a mensalidade para esta competência específica já existe
            if not Mensalidade.objects.filter(socio=socio, competencia=competencia).exists():
                valor = socio.categoria.valor_mensalidade
                dia_vencimento = socio.categoria.dia_vencimento

                if valor <= 0:
                    messages.warning(request, f'A categoria "{socio.categoria.nome}" não tem valor de mensalidade definido. Geração ignorada para algumas competências.')
                    continue
                
                try:
                    vencimento = competencia.replace(day=dia_vencimento)
                except ValueError:
                    import calendar
                    ultimo_dia = calendar.monthrange(competencia.year, competencia.month)[1]
                    vencimento = competencia.replace(day=ultimo_dia)

                novas_mensalidades_criadas.append(Mensalidade(
                    socio=socio,
                    competencia=competencia,
                    valor=valor,
                    data_vencimento=vencimento
                ))

        if novas_mensalidades_criadas:
            try:
                with transaction.atomic():
                    Mensalidade.objects.bulk_create(novas_mensalidades_criadas)
                messages.success(request, f'{len(novas_mensalidades_criadas)} mensalidades foram geradas com sucesso para {socio.nome}!')
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao gerar as mensalidades: {e}")
        else:
            messages.info(request, f'Nenhuma nova mensalidade precisava ser gerada para {socio.nome}.')
            
        return redirect('socios:lista_socios')
# --- Views de CategoriaSocio ---

class CategoriaSocioListView(LoginRequiredMixin, ListView):
    model = CategoriaSocio
    template_name = 'socios/categoria_list.html'
    context_object_name = 'categorias'
    def get_queryset(self):
        return CategoriaSocio.objects.filter(empresa=self.request.user.empresa)

class CategoriaSocioCreateView(LoginRequiredMixin, CreateView):
    model = CategoriaSocio
    form_class = CategoriaSocioForm
    template_name = 'socios/categoria_form.html'
    success_url = reverse_lazy('socios:lista_categorias')
    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

class CategoriaSocioUpdateView(LoginRequiredMixin, UpdateView):
    model = CategoriaSocio
    form_class = CategoriaSocioForm
    template_name = 'socios/categoria_form.html'
    success_url = reverse_lazy('socios:lista_categorias')
    def get_queryset(self):
        return CategoriaSocio.objects.filter(empresa=self.request.user.empresa)

class CategoriaSocioDeleteActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        categoria = get_object_or_404(CategoriaSocio, pk=pk, empresa=request.user.empresa)
        try:
            nome_categoria = categoria.nome
            categoria.delete()
            messages.success(request, f'A categoria "{nome_categoria}" foi excluída com sucesso.')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir a categoria "{categoria.nome}", pois ela está em uso.')
        return redirect('socios:lista_categorias')

# --- Views de Convenio ---

class ConvenioListView(LoginRequiredMixin, ListView):
    model = Convenio
    template_name = 'socios/convenio_list.html'
    context_object_name = 'convenios'
    def get_queryset(self):
        return Convenio.objects.filter(empresa=self.request.user.empresa)

class ConvenioCreateView(LoginRequiredMixin, CreateView):
    model = Convenio
    form_class = ConvenioForm
    template_name = 'socios/convenio_form.html'
    success_url = reverse_lazy('socios:lista_convenios')
    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

class ConvenioUpdateView(LoginRequiredMixin, UpdateView):
    model = Convenio
    form_class = ConvenioForm
    template_name = 'socios/convenio_form.html'
    success_url = reverse_lazy('socios:lista_convenios')
    def get_queryset(self):
        return Convenio.objects.filter(empresa=self.request.user.empresa)

class ConvenioDeleteActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        convenio = get_object_or_404(Convenio, pk=pk, empresa=request.user.empresa)
        try:
            nome_convenio = convenio.nome
            convenio.delete()
            messages.success(request, f'O convênio "{nome_convenio}" foi excluído com sucesso.')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir o convênio "{convenio.nome}", pois ele pode estar em uso.')
        return redirect('socios:lista_convenios')


# Adicione esta nova view no final do arquivo
class SocioPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        try:
            # Busca o sócio e seus dependentes, garantindo que pertence à empresa do usuário
            socio = get_object_or_404(Socio, pk=pk, empresa=request.user.empresa)
            dependentes = socio.dependentes.all()
            
            # Contexto de dados para o template
            context = {
                'socio': socio,
                'dependentes': dependentes,
                'empresa': request.user.empresa,
            }

            # Renderiza o template HTML para uma string
            html_string = render_to_string('socios/socio_pdf_template.html', context)
            
            # Gera o PDF a partir do HTML
            html = HTML(string=html_string, base_url=request.build_absolute_uri())
            pdf = html.write_pdf()

            # Cria a resposta HTTP com o conteúdo do PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            # Define o cabeçalho para ABRIR NO NAVEGADOR (inline)
            response['Content-Disposition'] = f'inline; filename="ficha_{socio.nome.lower().replace(" ", "_")}.pdf"'
            
            return response

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao gerar o PDF: {e}")
            return redirect('socios:lista_socios')
        
