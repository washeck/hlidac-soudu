from django.contrib import admin
from django.urls import path

from hlidac.views import IndexView, PridatRizeniView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("pridat-rizeni", PridatRizeniView.as_view(), name="pridat-rizeni"),
]
