import json
import re

from django import forms
from django.http import JsonResponse
from django.shortcuts import redirect, render

from scanner.models import Attendance, Ticket


class NameForm(forms.Form):
    name = forms.CharField(max_length=100)
    passphrase = forms.CharField(max_length=100)


# retrieve ticket data
def get_ticket_data(request):
    if request.method == 'GET':
        ticket_id = request.GET.get('id')

        is_valid_id = re.match(r"^GSB[A-Z1-9]{8}$", ticket_id)
        if is_valid_id is None:
            return JsonResponse({'success': 0, 'payload': 'invalid ticket reference'})

        try:
            ticket = Ticket.objects.get(uuid=ticket_id)
        except Ticket.DoesNotExist:
            return JsonResponse(
                {'success': 0, 'payload': 'nonexistent ticket reference'}
            )

        try:
            has_attendance = bool(ticket.attendance)
        except Ticket.attendance.RelatedObjectDoesNotExist:
            has_attendance = False

        return JsonResponse(
            {
                'success': 1,
                'payload': {
                    'name': ticket.name,
                    'type': str(ticket.kind),
                    'isCheckedIn': has_attendance,
                },
            }
        )


# check user in
def checkin(request):
    if request.method == 'POST':
        ticket_id = json.loads(request.body).get('id')

        is_valid_id = re.match(r"^GSB[A-Z1-9]{8}$", ticket_id)
        if is_valid_id is None:
            return JsonResponse({'success': 0, 'payload': 'invalid ticket reference'})

        try:
            ticket = Ticket.objects.get(uuid=ticket_id)
        except Ticket.DoesNotExist:
            return JsonResponse(
                {'success': 0, 'payload': 'nonexistent ticket reference'}
            )

        try:
            has_attendance = ticket.attendance
        except Ticket.attendance.RelatedObjectDoesNotExist:
            has_attendance = False

        if has_attendance:
            return JsonResponse(
                {
                    'success': 0,
                    'payload': f'user already checked in at {ticket.attendance.date}!',
                }
            )

        attendance = Attendance(
            ticket=ticket, checker=request.session.get('checker_name')
        )
        attendance.save()

        tickets_scanned = Ticket.objects.filter(attendance__isnull=False).count()

        return JsonResponse(
            {
                'success': 1,
                'payload': {'scanCount': tickets_scanned},
            }
        )


def set_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        form_valid = form.is_valid()
        pass_valid = form.cleaned_data["passphrase"] == os.environ['PASSPHRASE']
        if form_valid and pass_valid:
            request.session['checker_name'] = form.cleaned_data["name"]
            return redirect('scanner')
        else:
            return redirect('set_name')
    else:
        return render(request, 'setname.html')


def scanner(request):
    # if no name set then...
    if request.session.get('checker_name', None) is None:
        return redirect('set_name')
    return render(
        request,
        'index.html',
        {'tickets_scanned': Ticket.objects.filter(attendance__isnull=False).count()},
    )
