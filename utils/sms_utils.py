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




def verify_sms_otp(phone, otp_input):
    """
    Verify OTP entered by user for phone using VerificationCode model.
    Returns a dict with success status, message, phone, and customer.
    """
    try:
        otp_entry = VerificationCode.objects.filter(
            phone_number=phone,
            code=otp_input
        ).latest("timestamp")
    except VerificationCode.DoesNotExist:
        return {
            "success": False,
            "message": "Invalid OTP.",
            "phone": phone,
          
        }

    # Check validity (5 minutes)
    if not otp_entry.is_valid():
        return {
            "success": False,
            "message": "OTP expired.",
            "phone": phone,
        
        }

    # ✅ OTP verified → get customer
    

    return {
        "success": True,
        "message": "OTP verified successfully.",
        "phone": phone,
      
    }
