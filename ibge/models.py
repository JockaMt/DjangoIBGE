from django.db import models

# Modelo de tabelas 

class Regiao(models.Model):
    """
    Modelo para representar as regiões do Brasil (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)
    
    :param id: Identificador único da região
    :type id: int
    :param sigla: Sigla da região (ex: N, NE, CO, SE, S)
    :type sigla: string
    :param nome: Nome completo da região
    :type nome: string
    """
    id = models.IntegerField(primary_key=True, unique=True)
    sigla = models.TextField(max_length=2)
    nome = models.TextField(max_length=10)
    
    def __str__(self): 
        return self.nome

    
class Uf(models.Model):
    """
    Modelo para representar as Unidades Federativas (Estados e Distrito Federal)
    
    :param id: Identificador único da UF
    :type id: int
    :param sigla: Sigla da UF (ex: SP, RJ, MG)
    :type sigla: string
    :param nome: Nome completo da UF
    :type nome: string
    :param regiao: Região à qual a UF pertence
    :type regiao: Regiao
    """
    id = models.IntegerField(primary_key=True, unique=True)
    sigla = models.TextField(max_length=2)
    nome = models.TextField(max_length=20)
    regiao = models.ForeignKey(Regiao, on_delete=models.CASCADE)
    
    def __str__(self): 
        return self.nome


class RegiaoIntermediaria(models.Model):
    """
    Modelo para representar as Regiões Intermediárias (divisão territorial do IBGE)
    
    :param id: Identificador único da região intermediária
    :type id: int
    :param nome: Nome da região intermediária
    :type nome: string
    :param uf: Unidade Federativa à qual pertence
    :type uf: Uf
    """
    id = models.IntegerField(primary_key=True, unique=True)
    nome = models.TextField(max_length=20)
    uf = models.ForeignKey(Uf, on_delete=models.CASCADE)
    
    def __str__(self): 
        return self.nome
    

class RegiaoImediata(models.Model):
    """
    Modelo para representar as Regiões Imediatas (divisão territorial do IBGE)
    
    :param id: Identificador único da região imediata
    :type id: int
    :param nome: Nome da região imediata
    :type nome: string
    :param regiao_intermediaria: Região intermediária à qual pertence
    :type regiao_intermediaria: RegiaoIntermediaria
    """
    id = models.IntegerField(primary_key=True, unique=True)
    nome = models.TextField(max_length=20)
    regiao_intermediaria = models.ForeignKey(RegiaoIntermediaria, on_delete=models.CASCADE)
    
    def __str__(self): 
        return self.nome
     
        
class Mesorregiao(models.Model):
    """
    Modelo para representar as Mesorregiões (divisão territorial do IBGE)
    
    :param id: Identificador único da mesorregião
    :type id: int
    :param nome: Nome da mesorregião
    :type nome: string
    :param uf: Unidade Federativa à qual pertence
    :type uf: Uf
    """
    id = models.IntegerField(primary_key=True, unique=True)
    nome = models.TextField(max_length=20)
    uf = models.ForeignKey(Uf, on_delete=models.CASCADE)
    
    def __str__(self): 
        return self.nome


class Microrregiao(models.Model):
    """
    Modelo para representar as Microrregiões (divisão territorial do IBGE)
    
    :param id: Identificador único da microrregião
    :type id: int
    :param nome: Nome da microrregião
    :type nome: string
    :param mesorregiao: Mesorregião à qual pertence
    :type mesorregiao: Mesorregiao
    """
    id = models.IntegerField(primary_key=True, unique=True)
    nome = models.TextField(max_length=20)
    mesorregiao = models.ForeignKey(Mesorregiao, on_delete=models.CASCADE)
    
    def __str__(self): 
        return self.nome
    

class Estado(models.Model):
    """
    Modelo para representar os Estados brasileiros
    
    :param id: Identificador único do estado
    :type id: int
    :param sigla: Sigla do estado (ex: SP, RJ, MG)
    :type sigla: string
    :param nome: Nome completo do estado
    :type nome: string
    :param regiao: Região à qual o estado pertence
    :type regiao: Regiao
    """
    id = models.IntegerField(primary_key=True, unique=True)
    sigla = models.TextField(max_length=50)
    nome = models.TextField()
    regiao = models.ForeignKey(Regiao, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
    
    def __str__(self): 
        return self.nome


class Municipio(models.Model):
    """
    Modelo para representar os Municípios brasileiros
    
    :param id: Identificador único do município
    :type id: int
    :param nome: Nome do município
    :type nome: string
    :param microrregiao: Microrregião à qual o município pertence
    :type microrregiao: Microrregiao
    :param regiao_imediata: Região imediata à qual o município pertence
    :type regiao_imediata: RegiaoImediata
    """
    id = models.IntegerField(primary_key=True, unique=True)
    nome = models.TextField(max_length=50)
    microrregiao = models.ForeignKey(Microrregiao, on_delete=models.CASCADE, null=True, blank=True)
    regiao_imediata = models.ForeignKey(RegiaoImediata, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Município"
        verbose_name_plural = "Municípios"
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['microrregiao']),
            models.Index(fields=['regiao_imediata']),
        ]
    
    def __str__(self): 
        return self.nome
    
    
class Distrito(models.Model):
    """
    Modelo para representar os Distritos brasileiros
    
    :param id: Identificador único do distrito
    :type id: int
    :param nome: Nome do distrito
    :type nome: string
    :param municipio: Município ao qual o distrito pertence
    :type municipio: Municipio
    :param microrregiao: Microrregião à qual o distrito pertence
    :type microrregiao: Microrregiao
    :param mesorregiao: Mesorregião à qual o distrito pertence
    :type mesorregiao: Mesorregiao
    :param uf: Unidade Federativa à qual o distrito pertence
    :type uf: Uf
    :param regiao: Região à qual o distrito pertence
    :type regiao: Regiao
    :param regiao_imediata: Região imediata à qual o distrito pertence
    :type regiao_imediata: RegiaoImediata
    :param regiao_intermediaria: Região intermediária à qual o distrito pertence
    :type regiao_intermediaria: RegiaoIntermediaria
    """
    id = models.BigIntegerField(primary_key=True, unique=True)
    nome = models.TextField(max_length=50)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    microrregiao = models.ForeignKey(Microrregiao, on_delete=models.CASCADE)
    mesorregiao = models.ForeignKey(Mesorregiao, on_delete=models.CASCADE)
    uf = models.ForeignKey(Uf, on_delete=models.CASCADE)
    regiao = models.ForeignKey(Regiao, on_delete=models.CASCADE)
    regiao_imediata = models.ForeignKey(RegiaoImediata, on_delete=models.CASCADE)
    regiao_intermediaria = models.ForeignKey(RegiaoIntermediaria, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Distrito"
        verbose_name_plural = "Distritos"
    
    def __str__(self): 
        return self.nome
