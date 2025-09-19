from django.shortcuts import render, redirect
from django.contrib import messages
from customer.forms import OTPLoginForm
from utils.sms_utils import send_verification_sms
from customer.models import Customer

def otp_login_view(request):
    form = OTPLoginForm(request.POST or None)

    if request.method == "POST":
        phone = request.POST.get("phone")
        otp_input = request.POST.get("otp")
        name = "Customer"  # Can fetch from DB if exists

        if "send_otp" in request.POST:
            # Optional: get customer name if exists
            customer = Customer.objects.filter(phone=phone).first()
            if customer:
                name = customer.name or "Customer"

            result = send_verification_sms(phone, name)
            if result["success"]:
                messages.success(request, f"OTP sent to {phone}")
            else:
                messages.error(request, f"Failed to send OTP: {result.get('error')}")

    return render(request, "customer/otp_login.html", {"form": form})


from django.http import JsonResponse

def customer_api_root(request):
    return JsonResponse({
        "message": "Customer API Root",
        "endpoints": {
            "OTP Login (web view)": "/api/customer/otp-login/",
            "OTP API": "/api/customer/login_api/"
        }
    })