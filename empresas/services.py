import logging
import requests
import io
import zipfile
import csv
from tqdm import tqdm
from math import ceil
from django.conf import settings
from django.db import transaction
from .models import Empresa
import os

logging = logging.Logger(__name__)


class EmpresasService:
    """Service para importar as empresas"""
    
    URL = settings.ARCHIVE_URL
    
    @classmethod
    def get_data(cls):
        chunk_size = 1024 * 1024
        
        response = requests.get(cls.URL, stream=True)
        response.raise_for_status()
        
        if response.status_code != 200:
            raise Exception(f"Erro ao baixar: {response.status_code}")

        total_bytes = int(response.headers.get('Content-Length', 0))
        total_chunks = ceil(total_bytes / chunk_size) if total_bytes else None
        
        print(f"Tamanho total: {total_bytes} bytes")
        print(f"Chunks estimados: {total_chunks}")

        arquivo_zip = 'empresas_data.zip'
        
        if os.path.exists(arquivo_zip):
            print(f"O arquivo {arquivo_zip} já existe. Usando arquivo existente.")
        else:
            with open(arquivo_zip, 'wb') as f:
                for chunk in tqdm(response.iter_content(chunk_size), total=total_chunks, unit='MB', desc="Baixando"):
                    if chunk:
                        f.write(chunk)
            print("Download concluído.")

        print("Extraindo e processando dados...")
        cls._extract_and_process(arquivo_zip)
    
    @classmethod
    def _extract_and_process(cls, arquivo_zip):
        """Extrai o arquivo zip e processa os dados"""
        try:
            with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
                # Lista os arquivos no zip
                arquivos = zip_ref.namelist()
                print(f"Arquivos encontrados: {arquivos}")
                
                for arquivo in arquivos:
                    if arquivo.endswith('.csv') or arquivo.endswith('.CSV') or arquivo.endswith('.EMPRECSV'):
                        print(f"Processando arquivo: {arquivo}")
                        with zip_ref.open(arquivo) as csv_file:
                            cls._process_csv(csv_file)
                            
        except zipfile.BadZipFile:
            raise Exception("Arquivo zip corrompido ou inválido")
    
    @classmethod
    def _process_csv(cls, csv_file):
        """Processa o arquivo CSV e salva no banco de dados"""
        # Decodifica o arquivo CSV
        text_file = io.TextIOWrapper(csv_file, encoding='latin-1')  # Encoding comum para dados IBGE
        reader = csv.reader(text_file, delimiter=';')
        
        batch_size = 1000
        empresas_batch = []
        
        for row_num, row in enumerate(tqdm(reader, desc="Processando empresas")):
            try:
                empresa_data = cls._parse_empresa_row(row)
                if empresa_data:
                    empresas_batch.append(empresa_data)
                    
                    # Salva em lotes para melhor performance
                    if len(empresas_batch) >= batch_size:
                        cls._save_batch(empresas_batch)
                        empresas_batch = []
                        
            except Exception as e:
                logging.error(f"Erro na linha {row_num}: {e}")
                continue
        
        # Salva o último lote
        if empresas_batch:
            cls._save_batch(empresas_batch)
    
    @classmethod
    def _parse_empresa_row(cls, row):
        """Converte uma linha do CSV em dados da empresa"""
        try:
            # Verifica se a linha tem dados suficientes
            if len(row) < 7:
                return None
                
            # Baseado na estrutura do modelo Empresa
            return {
                'cnpj_basico': cls._parse_int(row[0]),
                'rasao_social': row[1].strip() if len(row) > 1 else '',
                'natureza_juridica': cls._parse_int(row[2]) if len(row) > 2 else 0,
                'clasificacao_do_responsavel': cls._parse_int(row[3]) if len(row) > 3 else 0,
                'capital_social': cls._parse_int(row[4]) if len(row) > 4 else 0,
                'porte': cls._parse_int(row[5]) if len(row) > 5 else 0,
                'ente_federativo_responsavel': row[6].strip() if len(row) > 6 and row[6].strip() else None,
            }
        except Exception as e:
            logging.error(f"Erro ao processar linha: {e}")
            return None
    
    @classmethod
    def _parse_int(cls, value_string):
        """Converte string para inteiro com limite para PostgreSQL"""
        if not value_string or value_string.strip() == '':
            return 0
        
        try:
            # Remove espaços e caracteres não numéricos
            clean_value = ''.join(filter(str.isdigit, str(value_string)))
            if not clean_value:
                return 0
            
            value = int(clean_value)
            # Limite para IntegerField no PostgreSQL: -2147483648 a 2147483647
            if value > 2147483647:
                return 2147483647
            elif value < -2147483648:
                return -2147483648
            return value
        except:
            return 0
    
    @classmethod
    def _save_batch(cls, empresas_batch):
        """Salva um lote de empresas no banco de dados"""
        try:
            with transaction.atomic():
                empresas_to_create = []
                
                for empresa_data in empresas_batch:
                    cnpj_basico = empresa_data['cnpj_basico']
                    
                    # Verifica se a empresa já existe
                    if not Empresa.objects.filter(cnpj_basico=cnpj_basico).exists():
                        empresas_to_create.append(Empresa(**empresa_data))
                
                # Bulk create para novas empresas
                if empresas_to_create:
                    Empresa.objects.bulk_create(empresas_to_create, ignore_conflicts=True)
                    print(f"Criadas {len(empresas_to_create)} novas empresas")
                    
        except Exception as e:
            logging.error(f"Erro ao salvar lote: {e}")
            # Tenta salvar individualmente em caso de erro
            cls._save_individually(empresas_batch)
    
    @classmethod
    def _save_individually(cls, empresas_batch):
        """Salva empresas individualmente em caso de erro no lote"""
        success_count = 0
        error_count = 0
        
        for empresa_data in empresas_batch:
            try:
                with transaction.atomic():
                    empresa, created = Empresa.objects.get_or_create(
                        cnpj_basico=empresa_data['cnpj_basico'],
                        defaults=empresa_data
                    )
                    if created:
                        success_count += 1
                    
            except Exception as e:
                error_count += 1
                logging.error(f"Erro ao salvar empresa {empresa_data.get('cnpj_basico')}: {e}")
                continue
        
        if success_count > 0:
            print(f"Salvamento individual: {success_count} empresas criadas")
        if error_count > 0:
            print(f"Salvamento individual: {error_count} empresas com erro")