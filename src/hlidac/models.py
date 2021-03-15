from django.db import models


class Rizeni(models.Model):
    spisova_znacka = models.CharField(max_length=20)
    predmet = models.CharField(max_length=100)
    url = models.URLField()
    zmena_ve_spisu = models.DateTimeField()
    ukoncene = models.BooleanField()

    def __str__(self):
        return self.spisova_znacka
