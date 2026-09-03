#!/usr/bin/env python
"""
Script para popular o banco de dados com dados iniciais
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clube_manager.settings')
sys.path.append(str(os.path.dirname(os.path.abspath(__file__))))

django.setup()

from django.contrib.auth import get_user_model
from core.models import Empresa, CategoriaSocio, Convenio, Socio, Dependente, ConfiguracaoSistema
from financeiro.models import Mensalidade, Caixa, PlanoDeContas

Usuario = get_user_model()


def criar_empresa_padrao():
    print("Criando empresa padrão...")
    empresa, _ = Empresa.objects.get_or_create(
        nome='Clube Campestre Exemplo',
        defaults={
            'responsavel': 'Administrador',
            'telefone': '(11) 3333-4444',
            'endereco': 'Rua Principal, 1000',
            'cidade': 'São Paulo',
            'estado': 'SP',
        }
    )
    print(f"Empresa criada: {empresa}")
    return empresa


def criar_configuracoes_iniciais(empresa):
    print("Criando configurações iniciais...")
    configuracoes = [
        ('NOME_CLUBE', 'Clube Campestre Exemplo', 'Nome oficial do clube'),
        ('DIA_VENCIMENTO_MENSALIDADE', '10', 'Dia do vencimento das mensalidades'),
        ('VALOR_MENSALIDADE_PADRAO', '150.00', 'Valor padrão da mensalidade'),
        ('PERMITIR_CANCELAMENTO_MENSALIDADE', 'True', 'Permite cancelamento de mensalidades'),
        ('DIAS_TOLERANCIA_MENSALIDADE', '5', 'Dias de tolerância para pagamento de mensalidades'),
        ('PERCENTUAL_JUROS_ATRASO', '2.0', 'Percentual de juros por mês de atraso'),
    ]
    for chave, valor, descricao in configuracoes:
        ConfiguracaoSistema.objects.get_or_create(
            empresa=empresa, chave=chave,
            defaults={'valor': valor, 'descricao': descricao}
        )
    print("Configurações iniciais criadas com sucesso!")


def criar_categorias_socio(empresa):
    print("Criando categorias de sócio...")
    categorias = [
        ('Básico', 'Acesso básico às instalações', Decimal('150.00'), 10),
        ('Familiar', 'Acesso completo para o sócio e dependentes', Decimal('250.00'), 10),
        ('Premium', 'Acesso VIP com benefícios exclusivos', Decimal('400.00'), 10),
    ]
    cats = {}
    for nome, desc, valor, dia in categorias:
        cat, _ = CategoriaSocio.objects.get_or_create(
            empresa=empresa, nome=nome,
            defaults={'descricao': desc, 'valor_mensalidade': valor, 'dia_vencimento': dia}
        )
        cats[nome] = cat
    print("Categorias criadas com sucesso!")
    return cats


def criar_convenios(empresa):
    print("Criando convênios...")
    convenio, _ = Convenio.objects.get_or_create(
        empresa=empresa, nome='Sem Convênio',
        defaults={'empresa_contato': '', 'telefone_contato': ''}
    )
    print("Convênios criados com sucesso!")
    return convenio


def criar_socios_exemplo(empresa, categoria, convenio):
    print("Criando sócios de exemplo...")
    socios_data = [
        {
            'num_registro': 1, 'nome': 'João Silva',
            'cpf': '12345678900', 'email': 'joao.silva@email.com',
            'data_nascimento': '1980-05-15', 'endereco': 'Rua das Flores, 123',
            'bairro': 'Centro', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01234-567',
        },
        {
            'num_registro': 2, 'nome': 'Maria Santos',
            'cpf': '98765432100', 'email': 'maria.santos@email.com',
            'data_nascimento': '1985-08-20', 'endereco': 'Avenida Principal, 456',
            'bairro': 'Jardins', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01456-789',
        },
        {
            'num_registro': 3, 'nome': 'Pedro Oliveira',
            'cpf': '45678912300', 'email': 'pedro.oliveira@email.com',
            'data_nascimento': '1975-12-10', 'endereco': 'Rua dos Ipês, 789',
            'bairro': 'Vila Nova', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '02345-678',
        },
    ]
    for socio_data in socios_data:
        socio, created = Socio.objects.get_or_create(
            cpf=socio_data['cpf'],
            defaults={
                **socio_data,
                'empresa': empresa,
                'categoria': categoria,
                'convenio': convenio,
                'situacao': 'ATIVO',
            }
        )
        if created:
            print(f"  Sócio criado: {socio.nome}")
    print("Sócios de exemplo criados com sucesso!")


def criar_mensalidades_exemplo():
    print("Criando mensalidades de exemplo...")
    socio = Socio.objects.first()
    if not socio:
        print("  Nenhum sócio encontrado. Pulando.")
        return

    for i in range(3):
        competencia = datetime.now().replace(day=1) - timedelta(days=30 * i)
        competencia = competencia.replace(day=1)
        vencimento = competencia.replace(day=10)
        valor = socio.categoria.valor_mensalidade

        mensalidade, created = Mensalidade.objects.get_or_create(
            socio=socio, competencia=competencia,
            defaults={
                'valor': valor,
                'data_vencimento': vencimento,
                'status': 'PENDENTE' if i == 0 else 'PAGA',
                'data_pagamento': vencimento if i > 0 else None,
            }
        )
        if created:
            print(f"  Mensalidade criada: {competencia.strftime('%m/%Y')} - R$ {valor}")
    print("Mensalidades de exemplo criadas com sucesso!")


def criar_admin(empresa):
    print("Criando usuario admin...")
    if not Usuario.objects.filter(email='admin@clubemanager.com').exists():
        Usuario.objects.create_superuser(
            username='admin',
            email='admin@clubemanager.com',
            password='admin123',
            empresa=empresa,
            nivel_acesso='ADMIN',
        )
        print("Admin criado: admin@clubemanager.com / admin123")
    else:
        print("Admin ja existe.")


def main():
    print("=" * 50)
    print("Iniciando população do banco de dados...")
    print("=" * 50)

    try:
        empresa = criar_empresa_padrao()
        criar_configuracoes_iniciais(empresa)
        cats = criar_categorias_socio(empresa)
        convenio = criar_convenios(empresa)
        criar_socios_exemplo(empresa, cats['Básico'], convenio)
        criar_mensalidades_exemplo()
        criar_admin(empresa)

        print("")
        print("=" * 50)
        print("Banco de dados populado com sucesso!")
        print("=" * 50)
        print("")
        print("Dados criados:")
        print("- Empresa padrao")
        print("- Configuracoes do sistema")
        print("- Categorias de socio")
        print("- Convenios")
        print("- Socios de exemplo")
        print("- Mensalidades de exemplo")
        print("- Usuario admin")
        print("")
        print("Usuario admin: admin@clubemanager.com")
        print("Senha: admin123")

    except Exception as e:
        print("")
        print("ERRO ao popular banco de dados: %s" % str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
