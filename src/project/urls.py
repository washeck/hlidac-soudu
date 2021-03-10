from django.contrib import admin
from django.urls import path

from hlidac.views import PridatRizeniView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("pridat-rizeni", PridatRizeniView.as_view(), name="pridat-rizeni"),
]
