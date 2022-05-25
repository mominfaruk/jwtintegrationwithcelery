from celery import shared_task
from django.core.mail import send_mail

# Create your tests here.


@shared_task
def email_send(email_subject, email_body, email_from, email_to):
    send_mail(email_subject, email_body, email_from,
              email_to, fail_silently=False)
    print('email sent')
