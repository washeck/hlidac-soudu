from django.contrib import admin

from hlidac.models import Rizeni


class RizeniAdmin(admin.ModelAdmin):
    list_display = ["spisova_znacka", "ukoncene", "zmena_ve_spisu"]


admin.site.register(Rizeni, RizeniAdmin)
