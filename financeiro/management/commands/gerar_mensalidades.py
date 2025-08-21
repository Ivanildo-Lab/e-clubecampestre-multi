# financeiro/management/commands/gerar_mensalidades.py

from django.core.management.base import BaseCommand, CommandError
from financeiro.models import Mensalidade

class Command(BaseCommand):
    help = 'Gera as mensalidades do mês atual para todos os sócios ativos.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando processo de geração de mensalidades...')
        try:
            num_criadas, num_ignoradas = Mensalidade.objects.gerar_mensalidades_para_ativos()
            
            if num_criadas > 0:
                self.stdout.write(self.style.SUCCESS(f'{num_criadas} novas mensalidades foram geradas com sucesso.'))
            else:
                self.stdout.write(self.style.SUCCESS('Nenhuma nova mensalidade a ser gerada.'))
            
            if num_ignoradas > 0:
                self.stdout.write(self.style.WARNING(f'{num_ignoradas} sócios foram ignorados (categoria sem valor de mensalidade).'))

        except Exception as e:
            raise CommandError(f'Ocorreu um erro: {e}')
