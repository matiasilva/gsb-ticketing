from datetime import date

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import PromoCode, TicketKind, User


class SignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    email = forms.EmailField()
    status = forms.CharField(disabled=True)


class NameChangeForm(forms.Form):
    new_name = forms.CharField(max_length=100, initial="")
    new_email = forms.EmailField(initial="")


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
    kind = forms.ModelChoiceField(queryset=None, initial=1)
    is_alc = forms.BooleanField(required=False)
    is_veg = forms.BooleanField(required=False)


class GuestLoginForm(forms.Form):
    email = forms.EmailField()
    passphrase = forms.CharField(max_length=30)


class GuestSignupForm(forms.Form):
    name = forms.CharField(max_length=100, initial="")
    surname = forms.CharField(max_length=100, initial="")
    email = forms.EmailField(initial="")
    passphrase = forms.CharField()
    matric_date = forms.DateField()
    pname = forms.CharField(max_length=100, required=False, initial="")
    psurname = forms.CharField(max_length=100, required=False, initial="")
    promocode = forms.CharField(max_length=30)

    def clean_promocode(self):
        data = self.cleaned_data['promocode']
        # 500 if no code defined
        alum_code = PromoCode.objects.get(enum='ALUM_SIGNUP')
        if data != alum_code.value:
            raise ValidationError("Incorrect alumni verification code")

        return data

    def clean_password(self):
        data = self.cleaned_data['passphrase']
        validate_password(data)

    def clean_email(self):
        data = self.cleaned_data['email']
        # check valid username
        if User.objects.filter(username=data).exists():
            raise ValidationError("A user with that email already exists!")

        return data
