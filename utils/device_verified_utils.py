from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from customer.models import Device
from customer.serializers import CustomerSerializer

MAX_DEVICES = getattr(settings, "MAX_DEVICES_PER_ACCOUNT", 2)

def device_check_after_login(request, customer, access_token, refresh_token):
    # read device data from request (client must send these)
    device_id = request.data.get("device_id") 
    device_name = request.data.get("device_name")
    device_type = request.data.get("device_type")    
    device_model = request.data.get("device_model")
    ip = request.META.get("REMOTE_ADDR")
    now = timezone.now()

    # active devices for customer
    active_qs = Device.objects.filter(customer=customer, status="active")

    # ✅ Define serializer once so it’s available in all cases
    customer_serializer = CustomerSerializer(customer)

    # Case A: same device (allow login)
    if device_id and active_qs.filter(device_id=device_id).exists():
        d = active_qs.get(device_id=device_id)
        d.last_login = now
        d.ip_address = ip or d.ip_address
        d.device_name = device_name or d.device_name
        d.device_model = device_model or d.device_model
        d.device_type = device_type or d.device_type
       # d.save(update_fields=["last_login", "ip_address", "device_name", "device_model", "device_type"])

        response = Response(
            {
                "status": 200,
                "message": "Success",
                "data": {
                    **customer_serializer.data,
                    "access_token": access_token,
                },
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="JWT_TOKEN",
            value=refresh_token,
            httponly=False,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7,
        )
        return response

    # Case B: room to add device (allow login and register)
    if active_qs.count() < MAX_DEVICES:
        Device.objects.create(
            customer=customer,
            device_id=device_id,
            device_name=device_name,
            ip_address=ip,
            last_login=now,
            device_model=device_model,
            device_type=device_type,
            status="active",
        )
        response = Response(
            {
                "status": 200,
                "message": "Success",
                "data": {
                    **customer_serializer.data,
                    "access_token": access_token,
                },
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="JWT_TOKEN",
            value=refresh_token,
            httponly=False,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7,
        )
        return response

    # Case C: limit reached and this is a new device -> DO NOT issue tokens
    devices = active_qs.order_by("-last_login")
    device_list = [
        {
            "id": d.device_id,
            "device_name": d.device_name or "Device Name",
            "device_model": d.device_model or "Device Model",
            "device_id": d.device_id or "Device Id",
            "device_type": getattr(d, "device_type", "MOBILE"),
            "login_time": d.last_login.strftime("%Y-%m-%d %H:%M:%S.%f") if d.last_login else None,
            "ip_address": d.ip_address or "IP Address",
            "status": d.status or "Status",
        }
        for d in devices
    ]

    return Response(
        {
            "status": 207,
            "message": "Device limit reached",
            "data": {
                "max_devices": MAX_DEVICES,
                "device_list": device_list,
                "customer": customer_serializer.data,
            },
        },
        status=207,
    )
