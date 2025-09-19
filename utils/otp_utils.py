import random
import requests
from urllib.parse import urlencode
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from customer.models import VerificationCode

# MSG91 Config
MSG91_API_URL = "https://api.msg91.com/api/sendhttp.php"
AUTH_KEY = "127168AI5mZVVT57f23e45"
SENDER_ID = "SKYLTD"
TEMPLATE_ID = "1407165460465145131"

# -----------------------
# Common OTP Utils
# -----------------------
def generate_otp():
    return str(random.randint(100000, 999999))

# -----------------------
# SMS OTP
# -----------------------
def send_verification_sms(phone_number, name="Customer"):
    otp = generate_otp()
    message = f"Dear {name}, Your Skylink Fibernet Verification Code is {otp}."

    VerificationCode.objects.update_or_create(
        phone_number=phone_number,
        defaults={"code": otp, "timestamp": timezone.now()}
    )

    params = {
        "authkey": AUTH_KEY,
        "mobiles": f"91{phone_number}",
        "message": message,
        "sender": SENDER_ID,
        "route": "4",
        "DLT_TE_ID": TEMPLATE_ID,
    }

    try:
        response = requests.get(MSG91_API_URL, params=urlencode(params))
        return {"success": response.status_code == 200, "response": response.text}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def verify_sms_otp(phone_number, otp_input):
    try:
        otp_record = VerificationCode.objects.get(phone_number=phone_number)
    except VerificationCode.DoesNotExist:
        return False, "No OTP sent to this number"

    if not otp_record.is_valid():
        return False, "OTP expired"
    if otp_record.code != otp_input:
        return False, "Invalid OTP"

    otp_record.delete()
    return True, "OTP verified successfully"

# -----------------------
# Email OTP
# -----------------------
_email_storage = {}

def send_verification_email(email, name="Customer"):
    otp = generate_otp()
    _email_storage[email] = otp

    try:
        subject = "Your OTP Code"
        message = f"Hello {name},\nYour OTP is: {otp}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_email_otp(email, otp_input):
    otp_saved = _email_storage.get(email)
    if not otp_saved:
        return False, "OTP expired or not generated."
    if otp_input == otp_saved:
        _email_storage.pop(email)
        return True, "OTP verified successfully."
    return False, "Invalid OTP"
