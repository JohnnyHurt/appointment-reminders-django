from __future__ import absolute_import

import arrow
import dramatiq

from django.conf import settings
from twilio.rest import Client

from .models import Appointment


# Uses credentials from the TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
# environment variables
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


@dramatiq.actor
def send_sms_reminder(appointment_id):
    """Send a reminder to a phone using Twilio SMS"""
    # Get our appointment from the database
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        # The appointment we were trying to remind someone about
        # has been deleted, so we don't need to do anything
        return

    appointment_time = arrow.get(appointment.time, appointment.time_zone.zone)
    body = 'Hola {0}!. Te recordamos que tienes una cita agendada en el área de {1} el {2} de {3} a las {4}'.format(
        appointment.name,
        appointment.area,
        appointment_time.format('DD'),
        appointment_time.format('MM'),
        appointment_time.format('h:mm a')    # DD-MM-YYY h:mm a
    )

    client.messages.create(
        body=body,
        to=appointment.phone_number,
        from_=settings.TWILIO_PHONE_NUMBER,
    )
