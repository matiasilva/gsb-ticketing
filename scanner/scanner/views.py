from django.http import JsonResponse
from django.shortcuts import redirect, render

from scanner.models import Attendance, Ticket


def checkin(request):
    if request.method == 'POST':
        ref = request.POST.get('ref')

        response_code = 0
        message = ""

        if validate_ticket_ref(ref) is None:
            message = 'Invalid ticket reference provided!'

        try:
            ticket = Ticket.objects.get(uuid=ref)
        except Ticket.DoesNotExist:
            message = 'Nonexistent ticket reference provided!'

        if ticket.attendance.exists():
            message = f'User already checked in at {ticket.attendance.date}!'

        attendance = Attendance(ticket=ticket, checker=request.user)
        attendance.save()

        # indicate success
        message = f'{ticket.name} ({ticket.uuid}) checked in'
        response_code = 1
        tickets_scanned = Ticket.objects.filter(attendance__isnull=False).count()

        return JsonResponse(
            {
                'code': response_code,
                'message': message,
                'tickets_scanned': tickets_scanned,
            }
        )

    else:
        return render(request, 'index.html')
