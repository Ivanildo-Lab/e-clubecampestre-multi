import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import CategoriaSocio, ConfiguracaoSistema, Empresa, Socio
from financeiro.models import Caixa, Conta, LancamentoCaixa, PlanoDeContas


class RelatorioContasBaixaTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nome='Clube Teste Relatórios')
        self.user = get_user_model().objects.create_user(
            username='rel_tester', password='123456', empresa=self.empresa
        )
        self.client.login(username='rel_tester', password='123456')

        self.caixa = Caixa.objects.create(empresa=self.empresa, nome='Caixa Geral')
        ConfiguracaoSistema.objects.create(
            empresa=self.empresa, chave='CAIXA_PADRAO_ID', valor=str(self.caixa.pk)
        )
        self.categoria = CategoriaSocio.objects.create(
            empresa=self.empresa, nome='Titular', valor_mensalidade=100.00
        )
        self.socio = Socio.objects.create(
            empresa=self.empresa,
            num_registro=1,
            categoria=self.categoria,
            nome='Maria Souza',
            data_nascimento=datetime.date(1985, 1, 1),
            cpf='111.222.333-44',
        )
        self.plano = PlanoDeContas.objects.create(
            empresa=self.empresa, codigo='1.01', tipo='RECEITA', nome='Receitas'
        )
        self.conta = Conta.objects.create(
            empresa=self.empresa,
            plano_de_contas=self.plano,
            socio=self.socio,
            descricao='Mensalidade avulsa',
            valor=100.00,
            data_vencimento=datetime.date(2026, 10, 10),
        )

    def test_tela_de_contas_envia_caixa_padrao_e_data_na_baixa(self):
        response = self.client.get(reverse('relatorios:contas'))
        self.assertEqual(response.status_code, 200)
        # Sem esses campos a baixa falhava ("Dados inválidos")
        self.assertContains(response, f'<input type="hidden" name="caixa" value="{self.caixa.pk}"')
        self.assertContains(response, 'name="data_pagamento"')

    def test_baixa_pela_tela_de_contas_oferece_o_recibo(self):
        response = self.client.post(
            reverse('financeiro:baixar_conta', kwargs={'pk': self.conta.pk}),
            {'caixa': self.caixa.pk, 'data_pagamento': '2026-11-16'},
        )
        self.conta.refresh_from_db()
        self.assertEqual(self.conta.status, 'PAGA')
        self.assertEqual(LancamentoCaixa.objects.filter(conta_origem=self.conta).count(), 1)
        self.assertIn('recibo=conta', response['Location'])
