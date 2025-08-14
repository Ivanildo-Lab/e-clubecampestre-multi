#!/usr/bin/env python
"""
Script para popular o banco de dados com dados iniciais
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clube_manager.settings')
sys.path.append('/home/z/my-project')

django.setup()

from django.contrib.auth import get_user_model
from socios.models import Socio, Dependente, InteracaoSocio
from financeiro.models import PlanoMensalidade, Mensalidade, CategoriaReceita, Receita, CategoriaDespesa, Despesa
from cobranca.models import TemplateCobranca
from eventos.models import Evento
from core.models import ConfiguracaoSistema

Usuario = get_user_model()


def criar_configuracoes_iniciais():
    """Criar configurações iniciais do sistema"""
    print("Criando configurações iniciais...")
    
    configuracoes = [
        {
            'chave': 'NOME_CLUBE',
            'valor': 'Clube Campestre Exemplo',
            'descricao': 'Nome oficial do clube'
        },
        {
            'chave': 'DIA_VENCIMENTO_MENSALIDADE',
            'valor': '10',
            'descricao': 'Dia do vencimento das mensalidades'
        },
        {
            'chave': 'VALOR_MENSALIDADE_PADRAO',
            'valor': '150.00',
            'descricao': 'Valor padrão da mensalidade'
        },
        {
            'chave': 'PERMITIR_CANCELAMENTO_MENSALIDADE',
            'valor': 'True',
            'descricao': 'Permite cancelamento de mensalidades'
        },
        {
            'chave': 'DIAS_TOLERANCIA_MENSALIDADE',
            'valor': '5',
            'descricao': 'Dias de tolerência para pagamento de mensalidades'
        },
        {
            'chave': 'PERCENTUAL_JUROS_ATRASO',
            'valor': '2.0',
            'descricao': 'Percentual de juros por mês de atraso'
        },
    ]
    
    for config_data in configuracoes:
        ConfiguracaoSistema.objects.get_or_create(
            chave=config_data['chave'],
            defaults={
                'valor': config_data['valor'],
                'descricao': config_data['descricao']
            }
        )
    
    print("Configurações iniciais criadas com sucesso!")


def criar_planos_mensalidade():
    """Criar planos de mensalidade padrão"""
    print("Criando planos de mensalidade...")
    
    planos = [
        {
            'nome': 'Plano Básico',
            'descricao': 'Acesso básico às instalações do clube',
            'valor': Decimal('150.00')
        },
        {
            'nome': 'Plano Familiar',
            'descricao': 'Acesso completo para o sócio e dependentes',
            'valor': Decimal('250.00')
        },
        {
            'nome': 'Plano Premium',
            'descricao': 'Acesso VIP com benefícios exclusivos',
            'valor': Decimal('400.00')
        }
    ]
    
    for plano_data in planos:
        PlanoMensalidade.objects.get_or_create(
            nome=plano_data['nome'],
            defaults=plano_data
        )
    
    print("Planos de mensalidade criados com sucesso!")


def criar_socios_exemplo():
    """Criar sócios de exemplo"""
    print("Criando sócios de exemplo...")
    
    socios_data = [
        {
            'nome_completo': 'João Silva',
            'cpf': '12345678900',
            'email': 'joao.silva@email.com',
            'telefone': '(11) 99999-8888',
            'data_nascimento': '1980-05-15',
            'endereco': 'Rua das Flores',
            'numero': '123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01234-567'
        },
        {
            'nome_completo': 'Maria Santos',
            'cpf': '98765432100',
            'email': 'maria.santos@email.com',
            'telefone': '(11) 98888-7777',
            'data_nascimento': '1985-08-20',
            'endereco': 'Avenida Principal',
            'numero': '456',
            'bairro': 'Jardins',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01456-789'
        },
        {
            'nome_completo': 'Pedro Oliveira',
            'cpf': '45678912300',
            'email': 'pedro.oliveira@email.com',
            'telefone': '(11) 97777-6666',
            'data_nascimento': '1975-12-10',
            'endereco': 'Rua dos Ipês',
            'numero': '789',
            'bairro': 'Vila Nova',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '02345-678'
        }
    ]
    
    for socio_data in socios_data:
        Socio.objects.get_or_create(
            cpf=socio_data['cpf'],
            defaults=socio_data
        )
    
    print("Sócios de exemplo criados com sucesso!")


def criar_mensalidades_exemplo():
    """Criar mensalidades de exemplo"""
    print("Criando mensalidades de exemplo...")
    
    socio = Socio.objects.first()
    plano = PlanoMensalidade.objects.first()
    
    if socio and plano:
        # Criar mensalidades para os últimos 3 meses
        for i in range(3):
            data_vencimento = datetime.now().date() - timedelta(days=30 * i)
            referencia = data_vencimento.strftime('%m/%Y')
            
            Mensalidade.objects.get_or_create(
                socio=socio,
                referencia=referencia,
                defaults={
                    'plano': plano,
                    'valor': plano.valor,
                    'data_vencimento': data_vencimento,
                    'status': 'PENDENTE' if i == 0 else 'PAGO',
                    'data_pagamento': data_vencimento if i > 0 else None,
                    'forma_pagamento': 'DINHEIRO' if i > 0 else None
                }
            )
    
    print("Mensalidades de exemplo criadas com sucesso!")


def criar_templates_cobranca():
    """Criar templates de cobrança"""
    print("Criando templates de cobrança...")
    
    templates = [
        {
            'nome': 'Cobrança Padrão',
            'tipo': 'EMAIL',
            'assunto': 'Lembrete de Mensalidade - Clube Campestre',
            'template': '''
Prezado(a) {{ socio.nome_completo }},

Esperamos que esteja tudo bem!

Este é um lembrete sobre sua mensalidade do Clube Campestre:

- Referência: {{ mensalidade.referencia }}
- Valor: R$ {{ mensalidade.valor }}
- Data de vencimento: {{ mensalidade.data_vencimento|date:"d/m/Y" }}

Caso já tenha realizado o pagamento, por favor, desconsidere este e-mail.

Para dúvidas ou mais informações, entre em contato conosco.

Atenciosamente,
Equipe do Clube Campestre
            ''',
            'variaveis_disponiveis': 'socio.nome_completo, mensalidade.referencia, mensalidade.valor, mensalidade.data_vencimento'
        },
        {
            'nome': 'Cobrança por Atraso',
            'tipo': 'EMAIL',
            'assunto': 'Mensalidade em Atraso - Clube Campestre',
            'template': '''
Prezado(a) {{ socio.nome_completo }},

Identificamos que sua mensalidade está em atraso:

- Referência: {{ mensalidade.referencia }}
- Valor: R$ {{ mensalidade.valor }}
- Data de vencimento: {{ mensalidade.data_vencimento|date:"d/m/Y" }}
- Dias de atraso: {{ mensalidade.dias_atraso }}

Por favor, regularize sua situação o mais breve possível para evitar juros.

Para realizar o pagamento ou negociar, entre em contato conosco.

Atenciosamente,
Equipe do Clube Campestre
            ''',
            'variaveis_disponiveis': 'socio.nome_completo, mensalidade.referencia, mensalidade.valor, mensalidade.data_vencimento, mensalidade.dias_atraso'
        }
    ]
    
    for template_data in templates:
        TemplateCobranca.objects.get_or_create(
            nome=template_data['nome'],
            defaults=template_data
        )
    
    print("Templates de cobrança criados com sucesso!")


def criar_eventos_exemplo():
    """Criar eventos de exemplo"""
    print("Criando eventos de exemplo...")
    
    eventos_data = [
        {
            'nome': 'Churrasco de Aniversário do Clube',
            'descricao': 'Venha celebrar mais um ano do nosso clube com muito churrasco, música e diversão para toda a família!',
            'tipo': 'SOCIAL',
            'data_inicio': datetime.now() + timedelta(days=30),
            'data_fim': datetime.now() + timedelta(days=30, hours=6),
            'local': 'Área de Churrasco do Clube',
            'capacidade_maxima': 200,
            'valor_ingresso_socio': Decimal('0.00'),
            'valor_ingresso_convidado': Decimal('50.00')
        },
        {
            'nome': 'Torneio de Tênis',
            'descricao': 'Torneio interno de tênis para sócios. Inscrições gratuitas!',
            'tipo': 'ESPORTIVO',
            'data_inicio': datetime.now() + timedelta(days=15),
            'data_fim': datetime.now() + timedelta(days=16),
            'local': 'Quadras de Tênis',
            'capacidade_maxima': 32,
            'valor_ingresso_socio': Decimal('0.00'),
            'valor_ingresso_convidado': Decimal('0.00')
        }
    ]
    
    for evento_data in eventos_data:
        Evento.objects.get_or_create(
            nome=evento_data['nome'],
            defaults=evento_data
        )
    
    print("Eventos de exemplo criados com sucesso!")


def main():
    """Função principal para popular o banco de dados"""
    print("Iniciando população do banco de dados...")
    
    try:
        criar_configuracoes_iniciais()
        criar_planos_mensalidade()
        criar_socios_exemplo()
        criar_mensalidades_exemplo()
        criar_templates_cobranca()
        criar_eventos_exemplo()
        
        print("\n✅ Banco de dados populado com sucesso!")
        print("\nDados criados:")
        print("- Configurações do sistema")
        print("- Planos de mensalidade")
        print("- Sócios de exemplo")
        print("- Mensalidades de exemplo")
        print("- Templates de cobrança")
        print("- Eventos de exemplo")
        
        print(f"\n👤 Usuário admin: admin@clubemanager.com")
        print("🔑 Senha: admin123")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular banco de dados: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()