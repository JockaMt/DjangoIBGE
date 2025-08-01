from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import transaction
import time


class Command(BaseCommand):
    help = 'Deleta todos os dados de uma tabela específica'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'tabela',
            type=str,
            help='Nome da tabela/modelo para deletar (ex: Uf, Municipio, Distrito, Regiao)'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a operação de deleção (obrigatório para segurança)'
        )
        parser.add_argument(
            '--app',
            type=str,
            default='ibge',
            help='Nome da app onde está o modelo (padrão: ibge)'
        )
    
    def handle(self, *args, **options):
        tabela = options['tabela']
        app_name = options['app']
        confirm = options['confirm']
        
        if not confirm:
            self.stdout.write(
                self.style.ERROR(
                    "ATENÇÃO: Esta operação irá deletar TODOS os dados da tabela!"
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "Use --confirm para confirmar que deseja prosseguir"
                )
            )
            return
        
        try:
            # Buscar o modelo na app especificada
            try:
                model = apps.get_model(app_name, tabela)
            except LookupError:
                raise CommandError(
                    f"Modelo '{tabela}' não encontrado na app '{app_name}'. "
                    f"Verifique se o nome está correto."
                )
            
            # Contar registros antes da deleção
            count_before = model.objects.count()
            
            if count_before == 0:
                self.stdout.write(
                    self.style.WARNING(f"A tabela {tabela} já está vazia.")
                )
                return
            
            self.stdout.write(
                self.style.WARNING(
                    f"Deletando {count_before} registros da tabela {tabela}..."
                )
            )
            
            start_time = time.time()
            
            # Usar transação para garantir atomicidade
            with transaction.atomic():
                deleted_count, details = model.objects.all().delete()
            
            elapsed_time = time.time() - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {deleted_count} registros deletados da tabela {tabela} "
                    f"em {elapsed_time:.2f} segundos"
                )
            )
            
            # Mostrar detalhes se houver relacionamentos deletados
            if len(details) > 1:
                self.stdout.write("\nDetalhes da deleção:")
                for model_name, count in details.items():
                    if count > 0:
                        self.stdout.write(f"  - {model_name}: {count} registros")
        
        except Exception as e:
            raise CommandError(f"Erro ao deletar dados: {e}")
