from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task(queue="cpu")
def send_email(email, key):
    html_str = render_to_string("passwordChange.html", {"link": key})
    message_text = strip_tags(html_str)

    send_mail(
        subject="Password reset",
        message=message_text,
        recipient_list=[email],
        html_message=html_str,
    )
