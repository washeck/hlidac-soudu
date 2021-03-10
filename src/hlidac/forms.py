from django import forms


class PridatRizeniForm(forms.Form):
    url = forms.URLField(
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Adresa řízení v systému InfoSoud",
                "size": 120,
            }
        ),
    )
