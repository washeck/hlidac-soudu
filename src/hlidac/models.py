from datetime import date

from django.db import models


class Rizeni(models.Model):
    spisova_znacka = models.CharField(max_length=20)
    predmet = models.CharField(max_length=100)
    url = models.URLField()
    zmena_ve_spisu = models.DateTimeField()
    ukoncene = models.BooleanField()
    datum_zahajeni = models.DateField()
    datum_skonceni = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.spisova_znacka

    def save(self, *args, **kwargs):
        self.ukoncene = bool(self.datum_skonceni)
        super().save(*args, **kwargs)

    @property
    def delka_rizeni(self):
        if self.datum_skonceni:
            konec = self.datum_skonceni
        else:
            konec = date.today()
        return konec - self.datum_zahajeni
