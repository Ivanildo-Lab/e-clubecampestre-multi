from django.urls import path
from .views import (MensalidadeListView, MensalidadeUpdateView,
                     GerarMensalidadesEmMassaView, BaixarMensalidadeView,
                    PlanoDeContasListView, PlanoDeContasCreateView,
                    PlanoDeContasUpdateView, PlanoDeContasDeleteView,
                    CaixaListView, CaixaCreateView,
                    CaixaUpdateView, CaixaDeleteView, FluxoDeCaixaView, MensalidadeDeleteView, BaixarContaView,
                    ContaListView, ContaCreateView, ContaUpdateView, ContaDeleteView,
                    LancamentoCaixaCreateView, LancamentoCaixaUpdateView, LancamentoCaixaDeleteView

                    )



app_name = 'financeiro'

urlpatterns = [
    path('mensalidades/', MensalidadeListView.as_view(), name='lista_mensalidades'),
    path('mensalidades/<int:pk>/baixar/', BaixarMensalidadeView.as_view(), name='baixar_mensalidade'),
    path('mensalidades/<int:pk>/editar/', MensalidadeUpdateView.as_view(), name='editar_mensalidade'),
    path('mensalidades/gerar-em-massa/', GerarMensalidadesEmMassaView.as_view(), name='gerar_mensalidades_massa'),
    path('plano-de-contas/', PlanoDeContasListView.as_view(), name='lista_plano_de_contas'),
    path('plano-de-contas/adicionar/', PlanoDeContasCreateView.as_view(), name='adicionar_plano_de_contas'),
    path('plano-de-contas/<int:pk>/editar/', PlanoDeContasUpdateView.as_view(), name='editar_plano_de_contas'),
    path('plano-de-contas/<int:pk>/excluir/', PlanoDeContasDeleteView.as_view(), name='excluir_plano_de_contas'),
    path('caixas/', CaixaListView.as_view(), name='lista_caixas'),
    path('caixas/adicionar/', CaixaCreateView.as_view(), name='adicionar_caixa'),
    path('caixas/<int:pk>/editar/', CaixaUpdateView.as_view(), name='editar_caixa'),
    path('caixas/<int:pk>/excluir/', CaixaDeleteView.as_view(), name='excluir_caixa'),
    path('fluxo-de-caixa/', FluxoDeCaixaView.as_view(), name='fluxo_de_caixa'),
    path('mensalidades/<int:pk>/excluir/', MensalidadeDeleteView.as_view(), name='excluir_mensalidade'),
    path('contas/', ContaListView.as_view(), name='lista_contas'),
    path('contas/adicionar/', ContaCreateView.as_view(), name='adicionar_conta'),
    path('contas/<int:pk>/editar/', ContaUpdateView.as_view(), name='editar_conta'),
    path('contas/<int:pk>/excluir/', ContaDeleteView.as_view(), name='excluir_conta'),
    path('contas/<int:pk>/baixar/', BaixarContaView.as_view(), name='baixar_conta'),
    path('fluxo-de-caixa/adicionar/', LancamentoCaixaCreateView.as_view(), name='adicionar_lancamento'),
    path('fluxo-de-caixa/<int:pk>/editar/', LancamentoCaixaUpdateView.as_view(), name='editar_lancamento'),
    path('fluxo-de-caixa/<int:pk>/excluir/', LancamentoCaixaDeleteView.as_view(), name='excluir_lancamento'),


]