from django.contrib import admin

from hlidac.models import Rizeni


class RizeniAdmin(admin.ModelAdmin):
    list_display = [
        "spisova_znacka",
        "predmet",
        "ukoncene",
        "zmena_ve_spisu",
        "delka_rizeni",
        "probehlo_odvolani",
    ]
    list_filter = ["ukoncene", "predmet", "soud"]


admin.site.register(Rizeni, RizeniAdmin)
