from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True)
    iso = models.CharField(max_length=2, blank=True, null=True)
    iso3 = models.CharField(max_length=3, blank=True, null=True)
    iso_numeric = models.IntegerField(blank=True, null=True)

    def _str_(self):
        return self.name