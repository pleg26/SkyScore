from django.db import models


class Country(models.Model):
    iso3 = models.CharField(max_length=3)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['iso3']
        db_table = 'competition_country'

    def __str__(self):
        text = self.iso3 + '-' + self.name
        if len(text) > 30:
            text = self.iso3 + '-' + self.name[0:26] + '...'
        return text


class Airfield(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.SET_DEFAULT, default=66, related_name='airfields')
    lon = models.FloatField(default=0)
    lat = models.FloatField(default=0)
    alt = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Airfield'
        verbose_name_plural = 'Airfields'
        ordering = ['country', 'code']
        db_table = 'competition_airfield'

    def __str__(self):
        text = self.code + ' - ' + self.name
        if len(text) > 30:
            text = text[0:30] + '...'
        return text
