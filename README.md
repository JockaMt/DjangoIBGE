# Sistema Django IBGE

## Visão Geral

Sistema Django para importação e gerenciamento de dados geográficos brasileiros da API oficial do IBGE. Importa estados, municípios e distritos com suas hierarquias geográficas.

## Características Principais

**Performance Otimizada**
- Operações em bulk com processamento de 500 registros por transação
- Cache de 89 horas para dados da API
- Redução de 40.000 para 25 queries (1.600x menos)
- Importação completa em 30-60 segundos

**Robustez**
- Tolerância a falhas para dados incompletos
- Validação de dados e tratamento de inconsistências
- Arquitetura de services com separação de responsabilidades

**Dados Suportados**
- 5 Regiões, 27 Estados + DF
- 5.570+ Municípios brasileiros
- 10.300+ Distritos com hierarquias completas

## Tecnologias

- Django 5.2.4 + Python 3.13
- PostgreSQL 15
- Docker + Docker Compose
- File-based caching system

## Como Usar

**Interface Web**
- Acesse `/estados/`, `/municipios/` ou `/distritos/`
- Clique em "Importar" para baixar dados da API

**Linha de Comando**
```bash
python manage.py import_ibge todos
python manage.py import_ibge estados
python manage.py delete_data Estado --confirm
```

**Django Admin**
- Acesse `/admin/` para visualizar e gerenciar dados
- Interface com busca, filtros e paginação

## Performance

| Métrica | Valor |
|---------|-------|
| Tempo de importação completa | 30-60 segundos |
| Municípios processados | 5.570+ |
| Distritos processados | 10.300+ |
| Redução de queries | 1.600x menos |
| Cache de API | 89 horas |
| Batch size | 500 registros |
