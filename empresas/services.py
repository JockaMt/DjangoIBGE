import logging
import requests
import io
from tqdm import tqdm
from math import ceil
from django.conf import settings

logging = logging.Logger(__name__)


class EmpresasService:
    """Service para importar as empresas"""
    
    URL = settings.ARCHIVE_URL
    
    @classmethod
    def get_data(self):
        chunk_size = 1024 * 1024
        
        response = requests.get(self.URL, stream=True)
        response.raise_for_status()
        
        if response.status_code != 200:
            raise Exception(f"Erro ao baixar: {response.status_code}")

        buffer = io.BytesIO()
        
        total_bytes = int(response.headers.get('Content-Length', 0))
        total_chunks = ceil(total_bytes / chunk_size) if total_bytes else None
        
        print(f"Tamanho total: {total_bytes} bytes")
        print(f"Chunks estimados: {total_chunks}")

        with open('arquivo.zip', 'wb') as f:
            for chunk in tqdm(response.iter_content(chunk_size), total=total_chunks, unit='MB'):
                f.write(chunk)
    
    