from datetime import date

from django import forms

from .models import TicketKind


class SignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    email = forms.EmailField()
    status = forms.CharField(disabled=True)


class BuyTicketForm(forms.Form):
    def __init__(self, tickets_qs, *args, **kwargs):
        extras = kwargs.pop('extras', 0)
        super(BuyTicketForm, self).__init__(*args, **kwargs)
        self.fields['kind'].queryset = tickets_qs
        for extra in extras:
            self.fields[extra.enum.lower()] = forms.BooleanField(
                initial=extra.opt_out,
                group='extras',
                label=extra.label,
                required=False,
                price=extra.price,
            )

    full_name = forms.CharField(max_length=100, initial="")
    email = forms.EmailField(initial="")
    dob = forms.DateField(initial="")
    kind = forms.ModelChoiceField(queryset=None, initial=1)

    def get_extras(self):
        return filter(lambda f: f.group == 'extras', self.fields.values())


class ManualLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=20)
