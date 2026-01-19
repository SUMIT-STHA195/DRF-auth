from django.core.cache import cache
from django.core.mail import send_mail
from tutorial.settings import EMAIL_HOST_USER
from django.contrib.auth import get_user_model
import secrets
from django.template.loader import get_template
from django.utils.html import strip_tags
User = get_user_model()


def generate_otp(user_email):
    otp = f"{secrets.randbelow(1000000):06d}"
    user = User.objects.get(email=user_email)
    cache_key = f"otp_forid_{user.id}"
    cache.set(cache_key, otp, timeout=200)
    return otp


def verify_otp(otp, email):
    user = User.objects.get(email=email)
    db_otp = cache.get(f"otp_forid_{user.id}")
    if db_otp == otp:
        return True


def send_otp_email(otp, recipient_email):
    context = {
        "receiver_name": "test",
        "otp": otp
    }
    template = get_template("email/otp_temp.html")
    convert_to_html_content = template.render(context)
    plain_message = strip_tags(convert_to_html_content)

    send_mail(
        subject="Reset password",
        message=plain_message,
        from_email=EMAIL_HOST_USER,
        recipient_list=[recipient_email],
        html_message=convert_to_html_content,
        fail_silently=False
    )
