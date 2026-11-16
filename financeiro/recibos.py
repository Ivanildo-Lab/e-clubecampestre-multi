# financeiro/recibos.py
"""
Montagem dos dados do RECIBO DE QUITAÇÃO.

O recibo é emitido após a baixa de mensalidades ou de contas a receber,
servindo de comprovação de quitação dos títulos para entrega ao cliente.
"""

from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from .models import Mensalidade, Conta


# ---------------------------------------------------------------------------
# Valor por extenso (pt-BR)
# ---------------------------------------------------------------------------

_UNIDADES = (
    '', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove',
    'dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis',
    'dezessete', 'dezoito', 'dezenove',
)
_DEZENAS = (
    '', '', 'vinte', 'trinta', 'quarenta', 'cinquenta',
    'sessenta', 'setenta', 'oitenta', 'noventa',
)
_CENTENAS = (
    '', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos',
    'seiscentos', 'setecentos', 'oitocentos', 'novecentos',
)


def _ate_mil(numero):
    """Extenso de 0 a 999 (retorna string vazia para 0)."""
    if numero <= 0:
        return ''
    if numero == 100:
        return 'cem'
    centenas, resto = divmod(numero, 100)
    partes = []
    if centenas:
        partes.append(_CENTENAS[centenas])
    if resto:
        if resto < 20:
            partes.append(_UNIDADES[resto])
        else:
            dezena, unidade = divmod(resto, 10)
            if unidade:
                partes.append(f'{_DEZENAS[dezena]} e {_UNIDADES[unidade]}')
            else:
                partes.append(_DEZENAS[dezena])
    return ' e '.join(partes)


def valor_por_extenso(valor):
    """Converte um valor monetário em extenso. Ex.: 1250.50 -> ..."""
    try:
        valor = Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception:
        return ''
    if valor < 0:
        return f'menos {valor_por_extenso(abs(valor))}'

    inteiro = int(valor)
    centavos = int((valor - inteiro) * 100)

    if inteiro == 0 and centavos == 0:
        return 'zero real'
    if inteiro == 0:
        return f'{_ate_mil(centavos)} centavo' + ('' if centavos == 1 else 's')

    grupos = []
    bilhoes, resto = divmod(inteiro, 1_000_000_000)
    milhoes, resto = divmod(resto, 1_000_000)
    milhares, unidade = divmod(resto, 1000)

    if bilhoes:
        grupos.append(f'{_ate_mil(bilhoes)} {"bilhão" if bilhoes == 1 else "bilhões"}')
    if milhoes:
        grupos.append(f'{_ate_mil(milhoes)} {"milhão" if milhoes == 1 else "milhões"}')
    if milhares:
        if milhares == 1:
            grupos.append('mil')
        else:
            grupos.append(f'{_ate_mil(milhares)} mil')
    if unidade:
        grupos.append(_ate_mil(unidade))

    if len(grupos) == 1:
        texto = grupos[0]
    else:
        # "mil duzentos e cinquenta" (sem "e" após "mil" antes de centenas)
        # "mil e cem" / "mil e quinze" / "um milhão e duzentos mil"
        centenas_grandes = (
            'duzentos', 'trezentos', 'quatrocentos', 'quinhentos',
            'seiscentos', 'setecentos', 'oitocentos', 'novecentos',
        )
        ultimo = grupos[-1]
        if len(grupos) == 2 and grupos[0] == 'mil' and ultimo.startswith(centenas_grandes):
            texto = ' '.join(grupos)
        else:
            texto = ', '.join(grupos[:-1]) + ' e ' + ultimo

    # "um milhão de reais" / "mil e um real" / "duzentos reais"
    if unidade == 1:
        texto += ' real'
    elif inteiro >= 1_000_000:
        texto += ' de reais'
    else:
        texto += ' reais'

    if centavos:
        texto += f' e {_ate_mil(centavos)} centavo' + ('' if centavos == 1 else 's')
    return texto


# ---------------------------------------------------------------------------
# Montagem do recibo
# ---------------------------------------------------------------------------

def _novo_grupo(socio):
    """Cria a estrutura de um recibo (um por cliente/sócio)."""
    if socio is None:
        cliente = {
            'nome': 'Cliente não identificado',
            'cpf': '',
            'endereco': '',
            'cidade': '',
            'registro': '',
        }
    else:
        endereco = ' - '.join([p for p in [socio.endereco, socio.bairro] if p])
        cliente = {
            'nome': socio.nome,
            'cpf': socio.cpf or '',
            'endereco': endereco,
            'cidade': ' - '.join([p for p in [socio.cidade, socio.estado] if p]),
            'registro': f'Matrícula nº {socio.num_registro}' if socio.num_registro else '',
        }
    return {
        'cliente': cliente,
        'titulos': [],
        'total': Decimal('0.00'),
        'data_pagamento': None,
        'forma_pagamento': None,
    }


def _agrupar(grupos, por_id, socio):
    if por_id not in grupos:
        grupos[por_id] = _novo_grupo(socio)
    return grupos[por_id]


def montar_recibo(request, tipo, ids):
    """
    Monta os dados do recibo de quitação.

    tipo: 'mensalidade' ou 'conta'
    ids:  lista de pks (só são considerados os títulos QUITADOS da empresa)
    Retorna dict com 'grupos' (um por cliente) ou None se nada for encontrado.
    """
    empresa = request.user.empresa
    grupos = {}

    if tipo == 'conta':
        itens = (
            Conta.objects
            .filter(id__in=ids, empresa=empresa, plano_de_contas__tipo='RECEITA', status='PAGA')
            .select_related('socio', 'plano_de_contas')
            .order_by('data_vencimento', 'id')
        )
        for conta in itens:
            grupo = _agrupar(grupos, f'conta-{conta.socio_id}', conta.socio)
            grupo['titulos'].append({
                'referencia': conta.descricao,
                'documento': conta.documento or f'#{conta.pk}',
                'vencimento': conta.data_vencimento,
                'valor': conta.valor,
            })
            grupo['total'] += conta.valor
            if conta.data_pagamento:
                grupo['data_pagamento'] = max(
                    filter(None, [grupo['data_pagamento'], conta.data_pagamento])
                )
    else:
        itens = (
            Mensalidade.objects
            .filter(id__in=ids, socio__empresa=empresa, status='PAGA')
            .select_related('socio', 'forma_pagamento')
            .order_by('data_vencimento', 'id')
        )
        for mensalidade in itens:
            grupo = _agrupar(grupos, f'socio-{mensalidade.socio_id}', mensalidade.socio)
            grupo['titulos'].append({
                'referencia': f"Mensalidade {mensalidade.competencia.strftime('%m/%Y')}",
                'documento': f'#{mensalidade.pk}',
                'vencimento': mensalidade.data_vencimento,
                'valor': mensalidade.valor,
            })
            grupo['total'] += mensalidade.valor
            if mensalidade.data_pagamento:
                grupo['data_pagamento'] = max(
                    filter(None, [grupo['data_pagamento'], mensalidade.data_pagamento])
                )
            if mensalidade.forma_pagamento and not grupo['forma_pagamento']:
                grupo['forma_pagamento'] = mensalidade.forma_pagamento.nome

    if not grupos:
        return None

    for grupo in grupos.values():
        grupo['total_extenso'] = valor_por_extenso(grupo['total'])
        grupo['qtd_titulos'] = len(grupo['titulos'])

    agora = timezone.now()
    return {
        'tipo': tipo,
        'titulo_documento': 'Recibo de Quitação de Mensalidades' if tipo == 'mensalidade'
                            else 'Recibo de Quitação de Conta a Receber',
        'grupos': list(grupos.values()),
        'empresa': empresa,
        'data_emissao': agora,
        'numero_recibo': f'RC-{agora:%Y%m%d%H%M%S}',
    }
