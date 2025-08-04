from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class Empresa(admin.ModelAdmin):
    list_display = (
        'cnpj_basico', 
        'rasao_social', 
        'natureza_juridica', 
        'clasificacao_do_responsavel',
        'capital_social',
        'porte',
        'ente_federativo_responsavel',
        )
    list_filter = (        
        'natureza_juridica',
        'clasificacao_do_responsavel',
        'capital_social',
        'porte',
        'ente_federativo_responsavel',
        )
    search_fields = ('rasao_social',)
    ordering = ('rasao_social',)