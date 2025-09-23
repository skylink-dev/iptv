import random
from django.core.mail import send_mail
from django.conf import settings
from urllib.parse import urlencode
from django.utils import timezone
from customer.models import VerificationCode

# In-memory OTP storage for demonstration
email_otp_storage = {}

# ------------------------------
# Generate OTP
# ------------------------------
def generate_otp():
    return str(random.randint(100000, 999999))


# ------------------------------
# Send OTP via Email
# ------------------------------
def send_verification_email(email, name="Customer"):
    """
    Send OTP to given email and store it in VerificationCode table.
    Returns dict with success/error.
    """
    otp = generate_otp()

    try:
        # Store or update OTP in DB
        VerificationCode.objects.update_or_create(
            email=email,
            defaults={"code": otp, "timestamp": timezone.now()}
        )

        # Send email
        subject = "Your OTP Code"
        message = f"Hello {name},\nYour OTP is: {otp}"
        from_email = settings.DEFAULT_FROM_EMAIL
        #send_mail(subject, message, from_email, [email])  // for testing i hide the code

        return {"success": True, "message": "OTP sent successfully."}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ------------------------------
# Verify OTP via Email
# ------------------------------
def verify_email_otp(email, otp_input):
    """
    Verify OTP entered by user for email using VerificationCode model.
    Returns a dict with success status, message, and email.
    """

     # ✅ Default OTP check (from settings)
    default_otp = getattr(settings, "DEFAULT_OTP", None)
    if default_otp and otp_input == default_otp:
        return {
            "success": True,
            "message": "OTP verified successfully (default OTP).",
            "email": email
        }
    try:
        otp_entry = VerificationCode.objects.filter(email=email, code=otp_input).latest("timestamp")
    except VerificationCode.DoesNotExist:
        return {
            "success": False,
            "message": "Invalid OTP.",
            "email": email
        }

    # Check validity (5 minutes)
    if not otp_entry.is_valid():
        return {
            "success": False,
            "message": "OTP expired.",
            "email": email
        }

    # ✅ OTP verified → delete entry after successful verification
    #otp_entry.delete()
    return {
        "success": True,
        "message": "OTP verified successfully.",
        "email": email
    }
