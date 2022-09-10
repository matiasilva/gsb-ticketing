from datetime import date

from django import forms

from .models import TicketKind


class SignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    email = forms.EmailField()
    status = forms.CharField(disabled=True)


class BuyTicketForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    kind = forms.ModelChoiceField(queryset=TicketKind.objects.all(), initial=1)
    dob = forms.DateField(initial="")
    is_own = forms.BooleanField(required=False)
