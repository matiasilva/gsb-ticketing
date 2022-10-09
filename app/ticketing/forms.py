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
        super(BuyTicketForm, self).__init__(*args, **kwargs)
        self.fields['kind'].queryset = tickets_qs

    full_name = forms.CharField(max_length=100, initial="")
    email = forms.EmailField(initial="")
    dob = forms.DateField(initial="")
    kind = forms.ModelChoiceField(queryset=None, initial=1)
