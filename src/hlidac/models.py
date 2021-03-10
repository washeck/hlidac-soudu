from django.db import models


class Rizeni(models.Model):
    spisova_znacka = models.CharField(max_length=20)
    url = models.URLField()

    def __str__(self):
        return self.spisova_znacka
