from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from .serializers import OTPRequestSerializer, OTPVerifySerializer, DeviceSerializer
from utils.sms_utils import send_verification_sms, verify_otp as verify_sms_otp
from utils.email_utils import send_verification_email, verify_email_otp

from .models import Device, Setting, Customer
from rest_framework import viewsets
from rest_framework.decorators import action
class SendOTPAPIView(APIView):

    def get_serializer(self, *args, **kwargs):
        """Provide default data for DRF Browsable API."""
        initial = {
            "phone": "9876543210",
            "email": "test@example.com",
            "code": "CUSTOMER123",
            "otp": "123456",
        }
        kwargs.setdefault("initial", initial)
        return OTPRequestSerializer(*args, **kwargs)

    def post(self, request):
        # merge defaults from serializer with request data
        serializer = OTPRequestSerializer(data=request.data or {})
        if serializer.is_valid():
            phone = serializer.validated_data.get("phone")
            email = serializer.validated_data.get("email")
            code = serializer.validated_data.get("code")

            if phone:
                send_verification_sms(phone)
                return Response({"status": 200, "message": f"OTP sent to phone {phone}"})

            elif email:
                send_verification_email(email)
                return Response({"status": 200, "message": f"OTP sent to email {email}"})

            elif code:
                try:
                    customer = Customer.objects.get(iptv_activation_code=code)
                    if customer.phone:
                        send_verification_sms(customer.phone)
                        return Response({"status": 200, "message": f"OTP sent to phone {customer.phone}"})
                    elif customer.email:
                        send_verification_email(customer.email)
                        return Response({"status": 200, "message": f"OTP sent to email {customer.email}"})
                    else:
                        return Response({"status": 400, "message": "No phone/email found for this code"})
                except Customer.DoesNotExist:
                    return Response({"status": 404, "message": "Customer not found"})

        return Response({"status": 400, "message": "Error", "data": serializer.errors})


class VerifyOTPAPIView(APIView):

    def get_serializer(self, *args, **kwargs):
        """Provide default data for DRF Browsable API."""
        initial = {
            "phone": "9876543210",
            "email": "test@example.com",
            "code": "CUSTOMER123",
            "otp": "123456",
        }
        kwargs.setdefault("initial", initial)
        return OTPVerifySerializer(*args, **kwargs)
        
    def post(self, request):
        # merge defaults from serializer with request data
        serializer = OTPVerifySerializer(data=request.data or {})
        if serializer.is_valid():
            phone = serializer.validated_data.get("phone")
            email = serializer.validated_data.get("email")
            code = serializer.validated_data.get("code")
            otp = serializer.validated_data.get("otp")

            if phone:
                if verify_sms_otp(phone, otp):
                    return Response({"status": 200, "message": "Phone OTP verified"})
                return Response({"status": 400, "message": "Invalid phone OTP"})

            elif email:
                if verify_email_otp(email, otp):
                    return Response({"status": 200, "message": "Email OTP verified"})
                return Response({"status": 400, "message": "Invalid email OTP"})

            elif code:
                try:
                    customer = Customer.objects.get(iptv_activation_code=code)
                    if customer.phone and verify_sms_otp(customer.phone, otp):
                        return Response({"status": 200, "message": "Code OTP verified via phone"})
                    elif customer.email and verify_email_otp(customer.email, otp):
                        return Response({"status": 200, "message": "Code OTP verified via email"})
                    else:
                        return Response({"status": 400, "message": "Invalid OTP for this code"})
                except Customer.DoesNotExist:
                    return Response({"status": 404, "message": "Customer not found"})

        return Response({"status": 400, "message": "Error", "data": serializer.errors})



class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    # ✅ Limit max devices per customer (e.g. 3 devices)
    def create(self, request, *args, **kwargs):
        customer_id = request.data.get("customer")
        max_devices = 3

        if customer_id:
            existing_devices = Device.objects.filter(customer_id=customer_id).count()
            if existing_devices >= max_devices:
                return Response(
                    {"error": f"Customer already has {max_devices} devices."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        customer_id = request.query_params.get('customer')
        if not customer_id:
            return Response({"error": "Customer ID required"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = Device.objects.filter(customer_id=customer_id).delete()
        return Response({"success": f"{deleted_count} devices deleted"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='replace')
    def replace_device(self, request):
        customer_id = request.data.get("customer")
        device_id = request.data.get("device_id")

        if not customer_id or not device_id:
            return Response({"error": "customer and device_id are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Delete existing device with the same device_id for this customer
        Device.objects.filter(customer_id=customer_id, device_id=device_id).delete()

        # Add the new device
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Device replaced successfully", "device": serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ReplaceDeviceAPIView(APIView):
    """
    Replace an existing device for a customer:
    1. Delete device specified by 'delete_existing_device_id'.
    2. Add a new device using provided details.
    """

    def post(self, request):
        customer_id = request.data.get("customer")
        delete_device_id = request.data.get("delete_existing_device_id")

        if not customer_id or not delete_device_id:
            return Response(
                {"error": "Both 'customer' and 'delete_existing_device_id' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 1: Delete existing device
        Device.objects.filter(customer_id=customer_id, device_id=delete_device_id).delete()

        # Step 2: Check max devices
        setting = Setting.objects.first()
        max_devices = setting.max_devices if setting else 3
        device_count = Device.objects.filter(customer_id=customer_id).count()
        if device_count >= max_devices:
            return Response(
                {"error": f"Customer already has maximum {max_devices} devices."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 3: Prepare new device data
        data = request.data.copy()
        data.pop("delete_existing_device_id", None)

        # Step 4: Save new device
        serializer = DeviceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": "Device replaced successfully.", "device": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
