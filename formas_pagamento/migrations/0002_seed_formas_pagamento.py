from django.db import migrations

def criar_formas_pagamento_padrao(apps, schema_editor):
    FormaPagamento = apps.get_model('formas_pagamento', 'FormaPagamento')
    Empresa = apps.get_model('core', 'Empresa')
    
    empresas = Empresa.objects.all()
    formas = ['PIX', 'Dinheiro', 'Cartao de Credito', 'Cartao de Debito', 'Boleto', 'Transferencia']
    
    for empresa in empresas:
        for nome in formas:
            FormaPagamento.objects.get_or_create(
                empresa=empresa,
                nome=nome,
                defaults={'ativo': True}
            )


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('formas_pagamento', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_formas_pagamento_padrao, reverse),
    ]
