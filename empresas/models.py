from django.db import models


class Empresa(models.Model):
    cnpj_basico = models.IntegerField(primary_key=True, unique=True)
    rasao_social = models.TextField(max_length=255)
    natureza_juridica = models.IntegerField()
    clasificacao_do_responsavel = models.IntegerField()
    capital_social = models.IntegerField()
    porte = models.IntegerField()
    ente_federativo_responsavel = models.TextField(null=True, blank=True)