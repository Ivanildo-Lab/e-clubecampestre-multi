# core/help_data.py

PARAMETROS_SISTEMA = [
    {
        'chave': 'CAIXA_PADRAO_ID',
        'titulo': 'Caixa Padrão para Baixas',
        'descricao': 'Define qual Caixa/Conta Bancária será pré-selecionado ao realizar a baixa de mensalidades ou outras contas. O valor deve ser o ID numérico do caixa.',
        'exemplo': 'Se o seu "Caixa Principal" tem o ID 1 na lista de caixas, o valor deste parâmetro deve ser "1".'
    },
    {
        'chave': 'TAXA_JUROS_MENSAL',
        'titulo': 'Taxa de Juros Mensal (%)',
        'descricao': 'Define a taxa de juros, em porcentagem, a ser aplicada sobre mensalidades em atraso. O sistema calcula os juros diários proporcionalmente a esta taxa.',
        'exemplo': 'Para uma taxa de 2% ao mês, o valor deste parâmetro deve ser "2.0".'
    },
    {
        'chave': 'PLANO_CONTAS_MENSALIDADE_ID',
        'titulo': 'Plano de Contas para Receita de Mensalidades',
        'descricao': 'Define qual item do Plano de Contas será usado para registrar a entrada de dinheiro vinda do pagamento de mensalidades. O valor deve ser o ID da conta.',
        'exemplo': 'Se a sua conta "Receita de Mensalidades" tem o ID 10, o valor deve ser "10".'
    },
    {
        'chave': 'PLANO_CONTAS_JUROS_ID',
        'titulo': 'Plano de Contas para Receita de Juros',
        'descricao': 'Define qual item do Plano de Contas será usado para registrar a entrada de dinheiro vinda de juros e multas por atraso. O valor deve ser o ID da conta.',
        'exemplo': 'Se a sua conta "Receita de Juros e Multas" tem o ID 11, o valor deve ser "11".'
    },
    # Futuramente, podemos adicionar mais parâmetros aqui
]