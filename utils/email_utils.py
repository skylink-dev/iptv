import random
from django.core.mail import send_mail
from django.conf import settings

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
    Send OTP to given email.
    Returns dict with success/error.
    """
    otp = generate_otp()
    email_otp_storage[email] = otp  # store OTP temporarily

    try:
        subject = "Your OTP Code"
        message = f"Hello {name},\nYour OTP is: {otp}"
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [email])
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ------------------------------
# Verify OTP via Email
# ------------------------------
def verify_email_otp(email, otp_input):
    """
    Verify OTP entered by user for email.
    """
    otp_saved = email_otp_storage.get(email)
    if not otp_saved:
        return False, "OTP expired or not generated."
    if otp_input == otp_saved:
        email_otp_storage.pop(email)  # remove OTP after successful verification
        return True, "OTP verified successfully."
    return False, "Invalid OTP."
