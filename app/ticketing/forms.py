from django import forms


class SignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    email = forms.EmailField()
    status = forms.CharField(disabled=True)


class TicketBuyForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    kind = forms.IntegerField()
    dob = forms.DateField()
