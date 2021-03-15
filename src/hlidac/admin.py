from django.contrib import admin

from hlidac.models import Rizeni


class RizeniAdmin(admin.ModelAdmin):
    list_display = ["spisova_znacka", "predmet", "ukoncene", "zmena_ve_spisu", "delka_rizeni"]
    list_filter = ["ukoncene", "predmet"]


admin.site.register(Rizeni, RizeniAdmin)
