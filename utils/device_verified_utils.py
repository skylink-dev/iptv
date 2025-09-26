from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from customer.models import Device, Profile
from customer.serializers import CustomerSerializer
import requests
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
            value=access_token,
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
            value=access_token,
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



def get_current_profile(request, customer):
    profile_code = request.headers.get("Current-Profile-Code")

    if not profile_code:
        return None

    return Profile.objects.filter(profile_code=profile_code, customer=customer).first()



def get_client_ip(request):
    """
    Returns the client's public IP if possible.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # The first IP is usually the public client IP
        ip = x_forwarded_for.split(",")[0].strip()
        # Sometimes proxies include private IPs; ignore those
        if ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172.16."):
            ip = None
    else:
        ip = request.META.get("REMOTE_ADDR")

    # Fallback: fetch public IP using external service (for testing if LAN/private IP)
    if not ip:
        try:
            ip = requests.get("https://api.ipify.org", timeout=3).text
        except:
            ip = None
    return ip
def get_weather(request):
    """
    Fetch weather using priority: lat/lon > city > public IP
    Always returns all fields. Missing data set to None.
    """
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    city = request.GET.get("city")

    # Fallback to public IP if no lat/lon and no city
    if (not lat or not lon) and not city:
        try:
            ip = requests.get("https://api.ipify.org", timeout=3).text
            if ip:
                ip_data = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
                lat = ip_data.get("lat")
                lon = ip_data.get("lon")
                city = ip_data.get("city")
        except:
            # Ignore errors, fields will stay None
            pass

    # Prepare default result
    result = {
        "city": city or None,
        "lat": float(lat) if lat else None,
        "lon": float(lon) if lon else None,
        "temperature": None,
        "humidity": None,
        "pressure": None,
        "weather": None,
        "wind_speed": None,
    }

    # If lat/lon or city available, fetch weather
    if (lat and lon) or city:
        try:
            owm_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {"appid": settings.OPENWEATHER_API_KEY, "units": "metric"}
            if lat and lon:
                params.update({"lat": lat, "lon": lon})
            elif city:
                params.update({"q": city})

            r = requests.get(owm_url, params=params, timeout=5)
            if r.status_code == 200:
                data = r.json()
                result.update({
                    "city": data.get("name") or result["city"],
                    "lat": data["coord"].get("lat") if data.get("coord") else result["lat"],
                    "lon": data["coord"].get("lon") if data.get("coord") else result["lon"],
                    "temperature": data["main"].get("temp") if data.get("main") else None,
                    "humidity": data["main"].get("humidity") if data.get("main") else None,
                    "pressure": data["main"].get("pressure") if data.get("main") else None,
                    "weather": data["weather"][0].get("description") if data.get("weather") else None,
                    "wind_speed": data["wind"].get("speed") if data.get("wind") else None,
                })
        except:
            # Ignore all exceptions, return defaults
            pass

    return result
