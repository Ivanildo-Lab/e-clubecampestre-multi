
#\financeiro\management\commands\gerar_mensalidades.py
from django.core.management.base import BaseCommand, CommandError
from financeiro.models import Mensalidade
from core.models import Empresa

class Command(BaseCommand):
    help = 'Gera as mensalidades para os próximos 12 meses para uma empresa específica.'

    def add_arguments(self, parser):
        parser.add_argument('empresa_id', type=int, help='O ID da empresa para a qual gerar as mensalidades.')

    def handle(self, *args, **options):
        empresa_id = options['empresa_id']
        try:
            empresa = Empresa.objects.get(pk=empresa_id)
            self.stdout.write(f'Iniciando processo para a empresa: {empresa.nome}...')
        except Empresa.DoesNotExist:
            raise CommandError(f'Empresa com ID "{empresa_id}" não encontrada.')

        try:
            num_criadas, num_ignoradas = Mensalidade.objects.gerar_mensalidades_para_ativos(empresa_id=empresa_id)
            
            if num_criadas > 0:
                self.stdout.write(self.style.SUCCESS(f'{num_criadas} novas mensalidades foram geradas com sucesso.'))
            else:
                self.stdout.write(self.style.SUCCESS('Nenhuma nova mensalidade precisava ser gerada.'))
            
            if num_ignoradas > 0:
                self.stdout.write(self.style.WARNING(f'{num_ignoradas} verificações foram ignoradas (sócio com categoria sem valor).'))
        except Exception as e:
            raise CommandError(f'Ocorreu um erro: {e}')
        