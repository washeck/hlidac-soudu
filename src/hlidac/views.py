from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import FormView, TemplateView

from hlidac.forms import PridatRizeniForm
from hlidac.models import Rizeni
from parser import load_rizeni


class IndexView(TemplateView):
    template_name = "hlidac/index.html"


class PridatRizeniView(FormView):
    form_class = PridatRizeniForm
    template_name = "hlidac/pridat-rizeni.html"
    success_url = "/"

    def form_valid(self, form):
        url = form.cleaned_data["url"]
        rizeni = load_rizeni(url)
        rizeni.set_predmet_rizeni()

        if "verified" not in self.request.POST:
            context_data = self.get_context_data(form=form)
            context_data["rizeni"] = rizeni
            return self.render_to_response(context_data)

        Rizeni.objects.create(
            url=url,
            spisova_znacka=rizeni.spisova_znacka,
            zmena_ve_spisu=rizeni.posledni_zmena,
            ukoncene=bool(rizeni.skonceni),
        )
        messages.info(self.request, f"Řízení {rizeni.spisova_znacka} bylo přidáno")
        return HttpResponseRedirect(self.get_success_url())
