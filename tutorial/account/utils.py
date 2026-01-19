from django.core.cache import cache
from django.core.mail import send_mail
from tutorial.settings import EMAIL_HOST_USER
from django.contrib.auth import get_user_model
import secrets
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
    send_mail(
        "Reset password",
        f"The OTP for your reset password request: {otp}",
        EMAIL_HOST_USER,
        [recipient_email],
        fail_silently=False
    )
