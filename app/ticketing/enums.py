from django.db import models


class UserStatus(models.IntegerChoices):
    GIRTON_UGRAD = 0, 'Girton Undergraduate'
    GIRTON_PGRAD = 1, 'Girton Postgraduate'
    GIRTON_STAFF = 2, 'Girton Staff'
    GIRTON_ALUM = 3, 'Girton Alumnus/a'
    UCAM_OTHER = 4, 'Cambridge University Member'
    # UCAM_UGRAD, UCAM_PGRAD, EXTERNAL


class UserAuthType(models.TextChoices):
    RAVEN = 0, 'Raven'
    MANUAL = 1, 'Manual'


class PaymentMethod(models.IntegerChoices):
    COLLEGE_BILL = 0, 'College Bill'
    BANK_TRANSFER = 1, 'Bank Transfer'
    CONCESSION = 2, 'Concession'


USER_TICKET_ALLOWANCE = {
    UserStatus.GIRTON_UGRAD: 3,
    UserStatus.GIRTON_PGRAD: 3,
    UserStatus.GIRTON_ALUM: 2,
    UserStatus.GIRTON_STAFF: 2,
    UserStatus.UCAM_OTHER: 2,
}

PAYMENT_METHOD_MAP = {
    UserStatus.GIRTON_UGRAD: PaymentMethod.COLLEGE_BILL,
    UserStatus.GIRTON_PGRAD: PaymentMethod.COLLEGE_BILL,
    UserStatus.GIRTON_STAFF: PaymentMethod.COLLEGE_BILL,
    UserStatus.GIRTON_ALUM: PaymentMethod.BANK_TRANSFER,
    UserStatus.UCAM_OTHER: PaymentMethod.BANK_TRANSFER,
}
