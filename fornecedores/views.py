from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Fornecedor
from .forms import FornecedorForm

class FornecedorListView(LoginRequiredMixin, ListView):
    model = Fornecedor
    template_name = 'fornecedores/fornecedor_list.html'
    context_object_name = 'fornecedores'
    paginate_by = 15

    def get_queryset(self):
        queryset = Fornecedor.objects.filter(empresa=self.request.user.empresa)
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(nome_fantasia__icontains=search_query) |
                Q(cpf_cnpj__icontains=search_query)
            )
        return queryset.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Fornecedores'
        context['search_query'] = self.request.GET.get('q', '')
        return context

class FornecedorCreateView(LoginRequiredMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'fornecedores/fornecedor_form.html'
    success_url = reverse_lazy('fornecedores:lista_fornecedores')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        messages.success(self.request, 'Fornecedor cadastrado com sucesso!')
        return super().form_valid(form)

class FornecedorUpdateView(LoginRequiredMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'fornecedores/fornecedor_form.html'
    success_url = reverse_lazy('fornecedores:lista_fornecedores')

    def get_queryset(self):
        return Fornecedor.objects.filter(empresa=self.request.user.empresa)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Fornecedor atualizado com sucesso!')
        return super().form_valid(form)

class FornecedorDeleteActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa=request.user.empresa)
        try:
            nome = fornecedor.nome
            fornecedor.delete()
            messages.success(request, f'O fornecedor "{nome}" foi excluído com sucesso.')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir o fornecedor. Ele pode estar vinculado a contas a pagar.')
        return redirect('fornecedores:lista_fornecedores')
    