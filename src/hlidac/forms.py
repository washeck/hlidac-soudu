from django import forms


class PridatRizeniForm(forms.Form):
    url = forms.URLField(label="Adresa InfoSoud")
