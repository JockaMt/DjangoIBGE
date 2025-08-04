from django.core.management.base import BaseCommand
from empresas.services import EmpresasService


class Command(BaseCommand):
    help = 'Importa dados das empresas do IBGE'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando importação das empresas...')
        
        try:
            EmpresasService.get_data()
            self.stdout.write(
                self.style.SUCCESS('Importação das empresas concluída com sucesso!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante a importação: {e}')
            )
