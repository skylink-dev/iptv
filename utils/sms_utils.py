import random
import requests
from urllib.parse import urlencode
from django.utils import timezone
from customer.models import VerificationCode

# MSG91 settings
# MSG91 API Configuration
MSG91_API_URL = "https://api.msg91.com/api/sendhttp.php"
AUTH_KEY = "127168AI5mZVVT57f23e45"  # Replace with your actual auth key
SENDER_ID = "SKYLTD"
TEMPLATE_ID = "1407165460465145131"

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_verification_sms(phone_number,  name="Customer"):
    """Send OTP via MSG91 and store in DB"""
    otp = generate_otp()
    message = f"Dear {name}, Your Skylink Fibernet Verification Code is {otp}."

    # Store or update OTP in database
    VerificationCode.objects.update_or_create(
        phone_number=phone_number,
        defaults={"code": otp, "timestamp": timezone.now()}
    )

    # Ensure phone number has country code
    phone_number_full = f"91{phone_number}"

    params = {
        "authkey": AUTH_KEY,
        "mobiles": phone_number_full,
        "message": message,
        "sender": SENDER_ID,
        "route": "4",
        "DLT_TE_ID": TEMPLATE_ID,
    }

    try:
        response = requests.get(MSG91_API_URL, params=urlencode(params))
        if response.status_code == 200:
            return {"success": True, "response": response.text}
        return {"success": False, "error": response.text}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def verify_otp(phone_number, otp_input):
    """Verify OTP"""
    try:
        otp_record = VerificationCode.objects.get(phone_number=phone_number)
    except VerificationCode.DoesNotExist:
        return False, "No OTP sent to this number"

    if not otp_record.is_valid():
        return False, "OTP expired"

    if otp_record.code != otp_input:
        return False, "Invalid OTP"

    otp_record.delete()  # Remove after successful verification
    return True, "OTP verified successfully"
