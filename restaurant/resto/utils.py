from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
def send_reservation_confirmation_email(customer_email, customer_name, reservation_date, table_id):
    subject = 'Reservation Confirmation'
    html_message = render_to_string('resto/reservation_confirmation_email.html', {
        'customer_name': customer_name,
        'reservation_date': reservation_date,
        'table_id': table_id,
    })
    plain_message = strip_tags(html_message)  # Strip HTML tags for plain text
    from_email = settings.EMAIL_HOST_USER  # Use the configured email host user
    send_mail(subject, plain_message, from_email, [customer_email], html_message=html_message)