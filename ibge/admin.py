from django.contrib import admin
from .models import (
    Regiao, Uf, RegiaoIntermediaria, RegiaoImediata, 
    Mesorregiao, Microrregiao, Estado, Municipio, Distrito
)

# Admin customizado para Regiões
@admin.register(Regiao)
class RegiaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sigla', 'nome')
    list_filter = ('sigla',)
    search_fields = ('nome', 'sigla')
    ordering = ('id',)

# Admin customizado para UFs
@admin.register(Uf)
class UfAdmin(admin.ModelAdmin):
    list_display = ('id', 'sigla', 'nome', 'regiao')
    list_filter = ('regiao',)
    search_fields = ('nome', 'sigla')
    ordering = ('sigla',)

# Admin customizado para Estados  
@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'sigla', 'regiao')
    list_filter = ('regiao',)
    search_fields = ('nome', 'sigla')
    ordering = ('sigla',)

# Admin customizado para Regiões Intermediárias
@admin.register(RegiaoIntermediaria)
class RegiaoIntermediariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'uf')
    list_filter = ('uf',)
    search_fields = ('nome',)
    ordering = ('nome',)

# Admin customizado para Regiões Imediatas
@admin.register(RegiaoImediata)
class RegiaoImediataAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'regiao_intermediaria')
    list_filter = ('regiao_intermediaria__uf',)
    search_fields = ('nome',)
    ordering = ('nome',)

# Admin customizado para Mesorregiões
@admin.register(Mesorregiao)
class MesorregiaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'uf')
    list_filter = ('uf',)
    search_fields = ('nome',)
    ordering = ('nome',)

# Admin customizado para Microrregiões
@admin.register(Microrregiao)
class MicroregiaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'mesorregiao')
    list_filter = ('mesorregiao__uf',)
    search_fields = ('nome',)
    ordering = ('nome',)

# Admin customizado para Municípios
@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'microrregiao', 'get_uf')
    list_filter = ('microrregiao__mesorregiao__uf',)
    search_fields = ('nome', 'id')
    ordering = ('nome',)
    list_per_page = 50  # Paginação para performance
    
    def get_uf(self, obj):
        return obj.microrregiao.mesorregiao.uf if obj.microrregiao and obj.microrregiao.mesorregiao else '-'
    get_uf.short_description = 'UF'

# Admin customizado para Distritos
@admin.register(Distrito)
class DistritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'municipio', 'get_uf')
    list_filter = ('uf',)
    search_fields = ('nome', 'id')
    ordering = ('nome',)
    list_per_page = 100  # Paginação para performance
    
    def get_uf(self, obj):
        return obj.uf if obj.uf else '-'
    get_uf.short_description = 'UF'
