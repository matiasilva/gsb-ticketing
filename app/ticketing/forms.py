from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import PromoCode, TicketKind


class SignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    email = forms.EmailField()
    status = forms.CharField(disabled=True)


class BuyTicketForm(forms.Form):
    def __init__(self, tickets_qs, *args, **kwargs):
        super(BuyTicketForm, self).__init__(*args, **kwargs)
        self.fields['kind'].queryset = tickets_qs
        for kind in tickets_qs:
            for extra in kind.optional_extras.all():
                self.fields[f'{extra.enum.lower()}_{kind.pk}'] = forms.BooleanField(
                    initial=extra.opt_out,
                    label=extra.label,
                    required=False,
                )

    full_name = forms.CharField(max_length=100, initial="")
    email = forms.EmailField(initial="")
    dob = forms.DateField(initial="")
    kind = forms.ModelChoiceField(queryset=None, initial=1)


class GuestLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=20)


class GuestSignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    email = forms.EmailField()
    matric_date = forms.DateField()
    pname = forms.CharField(max_length=100, required=False)
    psurname = forms.CharField(max_length=100, required=False)
    promocode = forms.CharField(max_length=30)

    def clean_promocode(self):
        data = self.cleaned_data['promocode']
        # 500 if no code defined
        alum_code = PromoCode.objects.get(enum='ALUM_SIGNUP')
        if data != alum_code.value:
            raise ValidationError("Incorrect alumni verification code")

        return data
