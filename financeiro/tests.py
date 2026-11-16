import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from django.urls import reverse

from core.models import CategoriaSocio, Empresa, Socio
from .models import Caixa, Conta, LancamentoCaixa, Mensalidade, PlanoDeContas
from .recibos import valor_por_extenso


class ValorPorExtensoTests(SimpleTestCase):
    def test_valores_comuns(self):
        self.assertEqual(valor_por_extenso(0), 'zero real')
        self.assertEqual(valor_por_extenso(1), 'um real')
        self.assertEqual(valor_por_extenso('0.50'), 'cinquenta centavos')
        self.assertEqual(valor_por_extenso(100), 'cem reais')
        self.assertEqual(valor_por_extenso(1000), 'mil reais')
        self.assertEqual(valor_por_extenso(1001), 'mil e um real')
        self.assertEqual(valor_por_extenso(1100), 'mil e cem reais')
        self.assertEqual(
            valor_por_extenso('1250.50'),
            'mil duzentos e cinquenta reais e cinquenta centavos',
        )
        self.assertEqual(valor_por_extenso(1000000), 'um milhão de reais')
        self.assertEqual(valor_por_extenso(1000001), 'um milhão e um real')
        self.assertEqual(valor_por_extenso('1250000'), 'um milhão e duzentos e cinquenta mil de reais')


class BaseFinanceiroTests(TestCase):
    """Cria uma empresa, um usuário logado e os dados mínimos do financeiro."""

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome='Clube Campestre Teste', cidade='São Paulo', estado='SP'
        )
        self.user = get_user_model().objects.create_user(
            username='tester', password='123456', empresa=self.empresa
        )
        self.client.login(username='tester', password='123456')

        self.categoria = CategoriaSocio.objects.create(
            empresa=self.empresa, nome='Titular', valor_mensalidade=150.00, dia_vencimento=10
        )
        self.socio = Socio.objects.create(
            empresa=self.empresa,
            num_registro=1,
            categoria=self.categoria,
            nome='João da Silva',
            data_nascimento=datetime.date(1990, 5, 20),
            cpf='123.456.789-00',
            endereco='Rua das Flores, 100',
            bairro='Centro',
            cidade='São Paulo',
            estado='SP',
        )
        self.caixa = Caixa.objects.create(empresa=self.empresa, nome='Caixa Secretaria')
        self.plano_receita = PlanoDeContas.objects.create(
            empresa=self.empresa, codigo='1.01', tipo='RECEITA', nome='Mensalidades'
        )
        self.plano_despesa = PlanoDeContas.objects.create(
            empresa=self.empresa, codigo='2.01', tipo='DESPESA', nome='Despesas'
        )

    def _mensalidade(self, status='PENDENTE'):
        return Mensalidade.objects.create(
            socio=self.socio,
            competencia=datetime.date(2026, 10, 1),
            valor=150.00,
            data_vencimento=datetime.date(2026, 10, 10),
            status=status,
            data_pagamento=datetime.date(2026, 10, 10) if status == 'PAGA' else None,
        )

    def _conta(self, tipo='RECEITA', status='PENDENTE'):
        return Conta.objects.create(
            empresa=self.empresa,
            plano_de_contas=self.plano_receita if tipo == 'RECEITA' else self.plano_despesa,
            socio=self.socio if tipo == 'RECEITA' else None,
            descricao='Mensalidade referente a outubro' if tipo == 'RECEITA' else 'Conta de luz',
            valor=250.00,
            data_vencimento=datetime.date(2026, 10, 10),
            status=status,
            data_pagamento=datetime.date(2026, 10, 12) if status == 'PAGA' else None,
        )


class ReciboMensalidadeTests(BaseFinanceiroTests):
    def test_pdf_do_recibo_e_baixavel(self):
        mensalidade = self._mensalidade(status='PAGA')
        url = reverse('financeiro:recibo_quitacao') + f'?tipo=mensalidade&ids={mensalidade.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_pdf_ignora_mensalidade_nao_quitada(self):
        mensalidade = self._mensalidade(status='PENDENTE')
        url = reverse('financeiro:recibo_quitacao') + f'?tipo=mensalidade&ids={mensalidade.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_pdf_agrupa_por_socio_em_varias_paginas(self):
        m1 = self._mensalidade(status='PAGA')
        m2 = Mensalidade.objects.create(
            socio=self.socio,
            competencia=datetime.date(2026, 11, 1),
            valor=150.00,
            data_vencimento=datetime.date(2026, 11, 10),
            status='PAGA',
            data_pagamento=datetime.date(2026, 11, 10),
        )
        url = reverse('financeiro:recibo_quitacao') + f'?tipo=mensalidade&ids={m1.pk},{m2.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_baixa_oferece_emissao_do_recibo(self):
        mensalidade = self._mensalidade(status='PENDENTE')
        url = reverse('financeiro:baixar_mensalidade', kwargs={'pk': mensalidade.pk})
        response = self.client.post(url, {'data_pagamento': '2026-11-16'})
        mensalidade.refresh_from_db()
        self.assertEqual(mensalidade.status, 'PAGA')
        self.assertIn('recibo=mensalidade', response['Location'])
        self.assertIn(f'recibo_ids={mensalidade.pk}', response['Location'])

    def test_baixa_em_lote_oferece_recibo_com_todos_os_ids(self):
        m1 = self._mensalidade(status='PENDENTE')
        m2 = Mensalidade.objects.create(
            socio=self.socio,
            competencia=datetime.date(2026, 12, 1),
            valor=150.00,
            data_vencimento=datetime.date(2026, 12, 10),
            status='ATRASADA',
        )
        url = reverse('financeiro:baixar_mensalidades_lote')
        response = self.client.post(url, {
            'mensalidades_ids': [str(m1.pk), str(m2.pk)],
            'data_pagamento': '2026-11-16',
        })
        self.assertEqual(Mensalidade.objects.filter(status='PAGA').count(), 2)
        self.assertIn('recibo=mensalidade', response['Location'])
        self.assertIn(f'recibo_ids={m1.pk},{m2.pk}', response['Location'])


class ReciboContaTests(BaseFinanceiroTests):
    def test_baixa_de_conta_a_receber_oferece_recibo(self):
        conta = self._conta(tipo='RECEITA')
        url = reverse('financeiro:baixar_conta', kwargs={'pk': conta.pk})
        response = self.client.post(url, {
            'caixa': self.caixa.pk,
            'data_pagamento': '2026-11-16',
        })
        conta.refresh_from_db()
        self.assertEqual(conta.status, 'PAGA')
        self.assertIn('recibo=conta', response['Location'])
        self.assertIn(f'recibo_ids={conta.pk}', response['Location'])
        self.assertEqual(LancamentoCaixa.objects.filter(conta_origem=conta).count(), 1)

    def test_baixa_de_conta_a_pagar_nao_oferece_recibo(self):
        conta = self._conta(tipo='DESPESA')
        url = reverse('financeiro:baixar_conta', kwargs={'pk': conta.pk})
        response = self.client.post(url, {
            'caixa': self.caixa.pk,
            'data_pagamento': '2026-11-16',
        })
        self.assertNotIn('recibo', response['Location'])

    def test_baixa_sem_caixa_nao_quita_a_conta(self):
        conta = self._conta(tipo='RECEITA')
        url = reverse('financeiro:baixar_conta', kwargs={'pk': conta.pk})
        response = self.client.post(url, {'data_pagamento': '2026-11-16'})
        conta.refresh_from_db()
        self.assertEqual(conta.status, 'PENDENTE')
        self.assertNotIn('recibo', response['Location'])

    def test_pdf_do_recibo_da_conta(self):
        conta = self._conta(tipo='RECEITA', status='PAGA')
        url = reverse('financeiro:recibo_quitacao') + f'?tipo=conta&ids={conta.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_pdf_ignora_conta_nao_quitada(self):
        conta = self._conta(tipo='RECEITA', status='PENDENTE')
        url = reverse('financeiro:recibo_quitacao') + f'?tipo=conta&ids={conta.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class TemplateListagemTests(BaseFinanceiroTests):
    """As telas de baixa precisam exibir a confirmação de impressão do recibo."""

    def test_lista_de_mensalidades_renderiza_a_confirmacao(self):
        self._mensalidade(status='PAGA')
        response = self.client.get(reverse('financeiro:lista_mensalidades'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Deseja imprimir Recibo de Quitação?')
        self.assertContains(response, 'reciboQuitacaoModal')
        # Botão de reemitir o recibo de mensalidade já paga
        self.assertContains(response, 'tipo=mensalidade&ids=')

    def test_lista_de_contas_a_receber_renderiza_modal_de_baixa_e_recibo(self):
        self._conta(tipo='RECEITA', status='PAGA')
        response = self.client.get(reverse('financeiro:lista_receber'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Deseja imprimir Recibo de Quitação?')
        self.assertContains(response, 'reciboQuitacaoModal')
        # Modal de baixa precisa enviar caixa + data (o form antigo não enviava)
        self.assertContains(response, 'js-baixa-conta-btn')
        self.assertContains(response, 'name="caixa"')
        self.assertContains(response, 'name="data_pagamento"')
        # Botão de reemitir o recibo da conta já quitada
        self.assertContains(response, 'tipo=conta&ids=')

    def test_lista_de_contas_a_pagar_nao_oferece_recibo(self):
        self._conta(tipo='DESPESA', status='PAGA')
        response = self.client.get(reverse('financeiro:lista_pagar'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'tipo=conta&ids=')
