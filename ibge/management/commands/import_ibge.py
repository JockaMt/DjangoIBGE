from django.core.management.base import BaseCommand, CommandError
from ibge.services import MunicipioImportService, DistritoImportService, EstadoImportService
import time


class Command(BaseCommand):
    help = 'Importa dados do IBGE (estados, municípios, distritos)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'tipo',
            type=str,
            choices=['estados', 'municipios', 'distritos', 'todos'],
            help='Tipo de dados para importar'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força reimportação mesmo se dados já existem'
        )
    
    def handle(self, *args, **options):
        tipo = options['tipo']
        start_time = time.time()
        
        try:
            if tipo == 'estados' or tipo == 'todos':
                self.stdout.write("Importando estados...")
                service = EstadoImportService()
                result = service.import_estados()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Estados: {result['created_estados']} criados, "
                        f"{result['created_regioes']} regiões criadas"
                    )
                )
            
            if tipo == 'municipios' or tipo == 'todos':
                self.stdout.write("Importando municípios...")
                service = MunicipioImportService()
                result = service.import_municipios()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Municípios: {result['created']} criados de {result['total_processed']} processados"
                    )
                )
            
            if tipo == 'distritos' or tipo == 'todos':
                self.stdout.write("Importando distritos...")
                service = DistritoImportService()
                result = service.import_distritos()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Distritos: {result['created']} criados de {result['total_processed']} processados"
                    )
                )
            
            elapsed_time = time.time() - start_time
            self.stdout.write(
                self.style.SUCCESS(
                    f"Importação concluída em {elapsed_time:.2f} segundos"
                )
            )
            
        except Exception as e:
            raise CommandError(f"Erro na importação: {e}")
