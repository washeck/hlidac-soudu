from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.views.generic import FormView, TemplateView

from hlidac.forms import PridatRizeniForm
from hlidac.models import Rizeni
from parser import SpisovaZnackaNeexistujeError, load_rizeni


class IndexView(TemplateView):
    template_name = "hlidac/index.html"


class PridatRizeniView(FormView):
    form_class = PridatRizeniForm
    template_name = "hlidac/pridat-rizeni.html"
    success_url = "/"

    def form_valid(self, form):
        url = form.cleaned_data["url"]
        try:
            rizeni = load_rizeni(url)
            rizeni.set_predmet_rizeni()
        except SpisovaZnackaNeexistujeError as e:
            form.add_error("url", str(e))
            return self.form_invalid(form)

        if "verified" not in self.request.POST:
            context_data = self.get_context_data(form=form)
            context_data["rizeni"] = rizeni
            return self.render_to_response(context_data)

        Rizeni.objects.create(
            url=url,
            spisova_znacka=rizeni.spisova_znacka,
            predmet=rizeni.predmet_rizeni,
            zmena_ve_spisu=rizeni.posledni_zmena,
            ukoncene=bool(rizeni.skonceni),
        )
        messages.info(self.request, f"Řízení {rizeni.spisova_znacka} bylo přidáno")
        return HttpResponseRedirect(self.get_success_url())
