from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy

from .models import FormaPagamento
from .forms import FormaPagamentoForm


class FormaPagamentoListView(LoginRequiredMixin, ListView):
    model = FormaPagamento
    template_name = 'formas_pagamento/formapagamento_list.html'
    context_object_name = 'formas_pagamento'

    def get_queryset(self):
        return FormaPagamento.objects.filter(empresa=self.request.user.empresa).order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Formas de Pagamento'
        return context


class FormaPagamentoCreateView(LoginRequiredMixin, CreateView):
    model = FormaPagamento
    form_class = FormaPagamentoForm
    template_name = 'formas_pagamento/formapagamento_form.html'
    success_url = reverse_lazy('formas_pagamento:lista_formas_pagamento')

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        messages.success(self.request, 'Forma de pagamento criada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Adicionar Forma de Pagamento'
        return context


class FormaPagamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = FormaPagamento
    form_class = FormaPagamentoForm
    template_name = 'formas_pagamento/formapagamento_form.html'
    success_url = reverse_lazy('formas_pagamento:lista_formas_pagamento')

    def get_queryset(self):
        return FormaPagamento.objects.filter(empresa=self.request.user.empresa)

    def form_valid(self, form):
        messages.success(self.request, 'Forma de pagamento atualizada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Forma de Pagamento'
        return context


class FormaPagamentoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        forma = get_object_or_404(FormaPagamento, pk=pk, empresa=request.user.empresa)
        try:
            nome = forma.nome
            forma.delete()
            messages.success(request, f'A forma de pagamento "{nome}" foi excluída com sucesso.')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir a forma de pagamento "{forma.nome}".')
        return redirect('formas_pagamento:lista_formas_pagamento')
