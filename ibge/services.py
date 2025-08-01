import logging
import requests
from typing import Dict, List, Optional
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings
from .models import Regiao, Estado, Municipio, Microrregiao, Mesorregiao, RegiaoImediata, RegiaoIntermediaria, Uf, Distrito


logger = logging.getLogger(__name__)


class IBGEAPIService:
    """Service para comunicação com API do IBGE"""
    
    BASE_URL = settings.EXTERNAL_API_URL
    CACHE_TIMEOUT = 320000
    
    @classmethod
    def get_data(cls, endpoint: str) -> List[Dict]:
        """Busca dados da API com cache"""
        url = f"{cls.BASE_URL}/{endpoint}"
        cache_key = f"api_data_{url.replace('/', '_').replace(':', '_')}"
        data = cache.get(cache_key)
        
        if data is None:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                cache.set(cache_key, data, cls.CACHE_TIMEOUT)
                logger.info(f"Dados de {len(data)} {endpoint} carregados da API")
            except requests.RequestException as e:
                logger.error(f"Erro ao buscar dados da API: {e}")
                raise
        else:
            logger.info(f"Usando cache: {len(data)} {endpoint}")
        
        return data
    
    @classmethod
    def get_municipios(cls) -> List[Dict]:
        """Busca municípios da API"""
        return cls.get_data("municipios")
    
    @classmethod
    def get_distritos(cls) -> List[Dict]:
        """Busca distritos da API"""
        return cls.get_data("distritos")
    
    @classmethod
    def get_estados(cls) -> List[Dict]:
        """Busca estados da API"""
        return cls.get_data("estados")


class DataValidationService:
    """Service para validação de dados"""
    
    @staticmethod
    def validate_municipio_data(data: Dict) -> Dict:
        """Valida e limpa dados do município"""
        if not data.get('id'):
            raise ValidationError("Município sem ID")
        
        if not data.get('nome'):
            raise ValidationError("Município sem nome")
        
        return {
            'id': int(data['id']),
            'nome': data['nome'].strip(),
        }
    
    @staticmethod
    def validate_distrito_data(data: Dict) -> Dict:
        """Valida e limpa dados do distrito"""
        if not data.get('id'):
            raise ValidationError("Distrito sem ID")
        
        if not data.get('nome'):
            raise ValidationError("Distrito sem nome")
        
        return {
            'id': int(data['id']),
            'nome': data['nome'].strip(),
        }
    
    @staticmethod
    def extract_hierarchy_data(municipio_data: Dict) -> Dict:
        """Extrai dados hierárquicos do município"""
        hierarchy = {
            'regiao': None,
            'uf': None,
            'mesorregiao': None,
            'microrregiao': None,
            'regiao_intermediaria': None,
            'regiao_imediata': None
        }
        
        try:
            if (municipio_data.get('microrregiao') and 
                municipio_data['microrregiao'].get('mesorregiao') and 
                municipio_data['microrregiao']['mesorregiao'].get('UF') and 
                municipio_data['microrregiao']['mesorregiao']['UF'].get('regiao')):
                
                regiao_data = municipio_data['microrregiao']['mesorregiao']['UF']['regiao']
                hierarchy['regiao'] = {
                    'id': regiao_data['id'],
                    'sigla': regiao_data['sigla'],
                    'nome': regiao_data['nome']
                }
                
                uf_data = municipio_data['microrregiao']['mesorregiao']['UF']
                hierarchy['uf'] = {
                    'id': uf_data['id'],
                    'sigla': uf_data['sigla'],
                    'nome': uf_data['nome'],
                    'regiao_id': regiao_data['id']
                }
                
                meso_data = municipio_data['microrregiao']['mesorregiao']
                hierarchy['mesorregiao'] = {
                    'id': meso_data['id'],
                    'nome': meso_data['nome'],
                    'uf_id': uf_data['id']
                }
                
                if municipio_data.get('microrregiao'):
                    micro_data = municipio_data['microrregiao']
                    hierarchy['microrregiao'] = {
                        'id': micro_data['id'],
                        'nome': micro_data['nome'],
                        'mesorregiao_id': meso_data['id']
                    }
                
                if municipio_data.get('regiao-imediata'):
                    rim_data = municipio_data['regiao-imediata']
                    hierarchy['regiao_imediata'] = {
                        'id': rim_data['id'],
                        'nome': rim_data['nome'],
                        'regiao_intermediaria_id': None
                    }
                    
                    if rim_data.get('regiao-intermediaria'):
                        ri_data = rim_data['regiao-intermediaria']
                        hierarchy['regiao_intermediaria'] = {
                            'id': ri_data['id'],
                            'nome': ri_data['nome'],
                            'uf_id': uf_data['id']
                        }
                        hierarchy['regiao_imediata']['regiao_intermediaria_id'] = ri_data['id']
                
        except (KeyError, TypeError) as e:
            logger.warning(f"Erro ao extrair hierarquia: {e}")
        
        return hierarchy


class MunicipioImportService:
    """Service para importação de municípios"""
    
    def __init__(self):
        self.api_service = IBGEAPIService()
        self.validation_service = DataValidationService()
        self.batch_size = 500
    
    def import_municipios(self) -> Dict:
        """Importa municípios da API para o banco"""
        try:
            raw_data = self.api_service.get_municipios()
            logger.info(f"Iniciando importação de {len(raw_data)} municípios")
            
            valid_municipios = []
            for raw_municipio in raw_data:
                try:
                    municipio_data = self.validation_service.validate_municipio_data(raw_municipio)
                    hierarchy = self.validation_service.extract_hierarchy_data(raw_municipio)
                    
                    valid_municipios.append({
                        'municipio': municipio_data,
                        'hierarchy': hierarchy
                    })
                except ValidationError as e:
                    logger.warning(f"Município inválido ignorado: {e}")
            
            with transaction.atomic():
                self._create_hierarchy_objects(valid_municipios)
                created_count = self._create_municipios(valid_municipios)
            
            logger.info(f"Importação concluída: {created_count} municípios criados")
            
            return {
                'success': True,
                'total_processed': len(raw_data),
                'valid_municipios': len(valid_municipios),
                'created': created_count
            }
            
        except Exception as e:
            logger.error(f"Erro na importação: {e}")
            raise
    
    def _create_hierarchy_objects(self, municipios_data: List[Dict]):
        """Cria objetos hierárquicos em bulk"""
        regioes_data = {}
        ufs_data = {}
        regioes_intermediarias_data = {}
        regioes_imediatas_data = {}
        mesorregioes_data = {}
        microrregioes_data = {}
        
        for item in municipios_data:
            hierarchy = item['hierarchy']
            
            if hierarchy['regiao']:
                regiao = hierarchy['regiao']
                regioes_data[regiao['id']] = regiao
            
            if hierarchy['uf']:
                uf = hierarchy['uf']
                ufs_data[uf['id']] = uf
            
            if hierarchy['regiao_intermediaria']:
                ri = hierarchy['regiao_intermediaria']
                regioes_intermediarias_data[ri['id']] = ri
            
            if hierarchy['regiao_imediata']:
                rim = hierarchy['regiao_imediata']
                regioes_imediatas_data[rim['id']] = rim
            
            if hierarchy['mesorregiao']:
                meso = hierarchy['mesorregiao']
                mesorregioes_data[meso['id']] = meso
            
            if hierarchy['microrregiao']:
                micro = hierarchy['microrregiao']
                microrregioes_data[micro['id']] = micro
        
        self._bulk_create_regioes(list(regioes_data.values()))
        self._bulk_create_ufs(list(ufs_data.values()))
        self._bulk_create_regioes_intermediarias(list(regioes_intermediarias_data.values()))
        self._bulk_create_regioes_imediatas(list(regioes_imediatas_data.values()))
        self._bulk_create_mesorregioes(list(mesorregioes_data.values()))
        self._bulk_create_microrregioes(list(microrregioes_data.values()))
    
    def _bulk_create_regioes(self, regioes_data: List[Dict]):
        """Cria regiões em bulk"""
        if not regioes_data:
            return
            
        existing_ids = set(Regiao.objects.values_list('id', flat=True))
        
        new_regioes = [
            Regiao(id=r['id'], sigla=r['sigla'], nome=r['nome'])
            for r in regioes_data
            if r['id'] not in existing_ids
        ]
        
        if new_regioes:
            Regiao.objects.bulk_create(new_regioes, batch_size=self.batch_size)
            logger.info(f"Criadas {len(new_regioes)} regiões")
    
    def _bulk_create_ufs(self, ufs_data: List[Dict]):
        """Cria UFs em bulk"""
        if not ufs_data:
            return
            
        existing_ids = set(Uf.objects.values_list('id', flat=True))
        
        new_ufs = [
            Uf(id=u['id'], sigla=u['sigla'], nome=u['nome'], regiao_id=u['regiao_id'])
            for u in ufs_data
            if u['id'] not in existing_ids
        ]
        
        if new_ufs:
            Uf.objects.bulk_create(new_ufs, batch_size=self.batch_size)
            logger.info(f"Criadas {len(new_ufs)} UFs")
    
    def _bulk_create_regioes_intermediarias(self, regioes_data: List[Dict]):
        """Cria regiões intermediárias em bulk"""
        if not regioes_data:
            return
            
        existing_ids = set(RegiaoIntermediaria.objects.values_list('id', flat=True))
        
        new_regioes = [
            RegiaoIntermediaria(id=r['id'], nome=r['nome'], uf_id=r['uf_id'])
            for r in regioes_data
            if r['id'] not in existing_ids
        ]
        
        if new_regioes:
            RegiaoIntermediaria.objects.bulk_create(new_regioes, batch_size=self.batch_size)
            logger.info(f"Criadas {len(new_regioes)} regiões intermediárias")
    
    def _bulk_create_regioes_imediatas(self, regioes_data: List[Dict]):
        """Cria regiões imediatas em bulk"""
        if not regioes_data:
            return
            
        existing_ids = set(RegiaoImediata.objects.values_list('id', flat=True))
        
        new_regioes = [
            RegiaoImediata(
                id=r['id'], 
                nome=r['nome'], 
                regiao_intermediaria_id=r['regiao_intermediaria_id']
            )
            for r in regioes_data
            if r['id'] not in existing_ids
        ]
        
        if new_regioes:
            RegiaoImediata.objects.bulk_create(new_regioes, batch_size=self.batch_size)
            logger.info(f"Criadas {len(new_regioes)} regiões imediatas")
    
    def _bulk_create_mesorregioes(self, mesorregioes_data: List[Dict]):
        """Cria mesorregiões em bulk"""
        if not mesorregioes_data:
            return
            
        existing_ids = set(Mesorregiao.objects.values_list('id', flat=True))
        
        new_mesorregioes = [
            Mesorregiao(id=m['id'], nome=m['nome'], uf_id=m['uf_id'])
            for m in mesorregioes_data
            if m['id'] not in existing_ids
        ]
        
        if new_mesorregioes:
            Mesorregiao.objects.bulk_create(new_mesorregioes, batch_size=self.batch_size)
            logger.info(f"Criadas {len(new_mesorregioes)} mesorregiões")
    
    def _bulk_create_microrregioes(self, microrregioes_data: List[Dict]):
        """Cria microrregiões em bulk"""
        if not microrregioes_data:
            return
            
        existing_ids = set(Microrregiao.objects.values_list('id', flat=True))
        
        new_microrregioes = [
            Microrregiao(id=m['id'], nome=m['nome'], mesorregiao_id=m['mesorregiao_id'])
            for m in microrregioes_data
            if m['id'] not in existing_ids
        ]
        
        if new_microrregioes:
            Microrregiao.objects.bulk_create(new_microrregioes, batch_size=self.batch_size)
            logger.info(f"Criadas {len(new_microrregioes)} microrregiões")
    
    def _create_municipios(self, municipios_data: List[Dict]) -> int:
        """Cria municípios em bulk"""
        existing_ids = set(Municipio.objects.values_list('id', flat=True))
        
        municipios_to_create = []
        for item in municipios_data:
            municipio = item['municipio']
            hierarchy = item['hierarchy']
            
            if municipio['id'] not in existing_ids:
                microrregiao_id = hierarchy['microrregiao']['id'] if hierarchy['microrregiao'] else None
                regiao_imediata_id = hierarchy['regiao_imediata']['id'] if hierarchy['regiao_imediata'] else None
                
                municipios_to_create.append(Municipio(
                    id=municipio['id'],
                    nome=municipio['nome'],
                    microrregiao_id=microrregiao_id,
                    regiao_imediata_id=regiao_imediata_id
                ))
        
        if municipios_to_create:
            Municipio.objects.bulk_create(municipios_to_create, batch_size=self.batch_size)
        
        return len(municipios_to_create)


class DistritoImportService:
    """Service para importação de distritos"""
    
    def __init__(self):
        self.api_service = IBGEAPIService()
        self.validation_service = DataValidationService()
        self.batch_size = 500
    
    def import_distritos(self) -> Dict:
        """Importa distritos da API para o banco"""
        try:
            municipios_map = self._load_municipios_map()
            raw_data = self.api_service.get_distritos()
            existing_distritos = set(Distrito.objects.values_list('id', flat=True))
            
            logger.info(f"Analisando {len(raw_data)} distritos")
            
            distritos_to_create = []
            for distrito_data in raw_data:
                if distrito_data['id'] in existing_distritos:
                    continue
                
                try:
                    distrito = self.validation_service.validate_distrito_data(distrito_data)
                    municipio_id = distrito_data['municipio']['id']
                    municipio_obj = municipios_map.get(municipio_id)
                    
                    if municipio_obj and municipio_obj.microrregiao:
                        distritos_to_create.append(Distrito(
                            id=distrito['id'],
                            nome=distrito['nome'],
                            municipio=municipio_obj,
                            microrregiao=municipio_obj.microrregiao,
                            mesorregiao=municipio_obj.microrregiao.mesorregiao,
                            uf=municipio_obj.microrregiao.mesorregiao.uf,
                            regiao=municipio_obj.microrregiao.mesorregiao.uf.regiao,
                            regiao_imediata=municipio_obj.regiao_imediata,
                            regiao_intermediaria=municipio_obj.regiao_imediata.regiao_intermediaria if municipio_obj.regiao_imediata else None
                        ))
                except ValidationError as e:
                    logger.warning(f"Distrito inválido ignorado: {e}")
                except Exception as e:
                    logger.error(f"Erro ao processar distrito {distrito_data.get('nome')}: {e}")
            
            created_count = 0
            if distritos_to_create:
                with transaction.atomic():
                    for i in range(0, len(distritos_to_create), self.batch_size):
                        batch = distritos_to_create[i:i + self.batch_size]
                        Distrito.objects.bulk_create(batch, batch_size=self.batch_size)
                        created_count += len(batch)
                        logger.info(f"Salvos {min(i + self.batch_size, len(distritos_to_create))}/{len(distritos_to_create)}")
            
            logger.info(f"Importação de distritos concluída: {created_count} criados")
            
            return {
                'success': True,
                'total_processed': len(raw_data),
                'created': created_count
            }
            
        except Exception as e:
            logger.error(f"Erro na importação de distritos: {e}")
            raise
    
    def _load_municipios_map(self) -> Dict:
        """Carrega mapa de municípios com relações"""
        logger.info("Carregando municípios do banco")
        
        municipios = Municipio.objects.select_related(
            'microrregiao__mesorregiao__uf__regiao',
            'regiao_imediata__regiao_intermediaria'
        ).all()
        
        return {m.id: m for m in municipios}


class EstadoImportService:
    """Service para importação de estados"""
    
    def __init__(self):
        self.api_service = IBGEAPIService()
        self.batch_size = 500
    
    def import_estados(self) -> Dict:
        """Importa estados da API para o banco"""
        try:
            raw_data = self.api_service.get_estados()
            logger.info(f"Iniciando importação de {len(raw_data)} estados")
            
            with transaction.atomic():
                regioes_data = {}
                estados_data = []
                
                for estado in raw_data:
                    regiao_data = estado['regiao']
                    regioes_data[regiao_data['id']] = regiao_data
                    estados_data.append(estado)
                
                # Criar regiões primeiro
                existing_regioes = set(Regiao.objects.values_list('id', flat=True))
                new_regioes = [
                    Regiao(id=r['id'], sigla=r['sigla'], nome=r['nome'])
                    for r in regioes_data.values()
                    if r['id'] not in existing_regioes
                ]
                
                if new_regioes:
                    Regiao.objects.bulk_create(new_regioes, batch_size=self.batch_size)
                    logger.info(f"Criadas {len(new_regioes)} regiões")
                
                # Criar estados
                existing_estados = set(Estado.objects.values_list('id', flat=True))
                new_estados = [
                    Estado(
                        id=e['id'],
                        sigla=e['sigla'],
                        nome=e['nome'],
                        regiao_id=e['regiao']['id']
                    )
                    for e in estados_data
                    if e['id'] not in existing_estados
                ]
                
                if new_estados:
                    Estado.objects.bulk_create(new_estados, batch_size=self.batch_size)
                    logger.info(f"Criados {len(new_estados)} estados")
            
            return {
                'success': True,
                'total_processed': len(raw_data),
                'created_estados': len(new_estados) if 'new_estados' in locals() else 0,
                'created_regioes': len(new_regioes) if 'new_regioes' in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"Erro na importação de estados: {e}")
            raise
