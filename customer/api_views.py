from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from .serializers import OTPRequestSerializer, OTPVerifySerializer, ReplaceDeviceSerializer, ProfileSerializer
from utils.sms_utils import send_verification_sms, verify_sms_otp

from utils.email_utils import send_verification_email, verify_email_otp
from utils.device_verified_utils import device_check_after_login

from .models import Device, Setting, Customer, Profile
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import os
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

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
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get("phone")
            email = serializer.validated_data.get("email")
            code = serializer.validated_data.get("code")
            otp = serializer.validated_data.get("otp")

            customer = None
            result = None

            # 🔹 Phone OTP flow
            if phone:
                customer = Customer.objects.filter(phone=phone).first()
                result = verify_sms_otp(phone, otp)
                otp_failed_status = 400  # or 400 if you prefer

            # 🔹 Email OTP flow
            elif email:
                customer = Customer.objects.filter(email=email).first()
                result = verify_email_otp(email, otp)
                otp_failed_status = 400

            # 🔹 Code-based flow
            elif code:
                customer = Customer.objects.filter(iptv_activation_code=code).first()
                if customer:
                    if customer.phone:
                        result = verify_sms_otp(customer.phone, otp)
                    elif customer.email:
                        result = verify_email_otp(customer.email, otp)
                    else:
                        return Response(
                            {"status": 400, "message": "No contact info found", "data": None},
                            status=400,
                        )
                otp_failed_status = 400

            # 🔹 Customer not found
            if not customer:
                return Response(
                    {"status": 404, "message": "Customer not found", "data": None},
                    status=404,
                )
            
            # if customer.account_status != "active":
            #     return Response(
            #         {
            #             "status": 403,
            #             "message": f"Account is {customer.account_status}, please contact support.",
            #         },
            #         status=403,
            #     )

            # 🔹 OTP failed
            if not result or not result.get("success"):
                return Response(
                    {"status": otp_failed_status, "message": result.get("message", "OTP failed"), "data": None},
                    status=otp_failed_status,
                )
            
            

            # ✅ OTP success → call device check to handle max devices
            refresh = RefreshToken.for_user(customer)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return device_check_after_login(request, customer, access_token, refresh_token)

        else:
            # ❌ Validation failed
            error_messages = []
            for field, errors in serializer.errors.items():
                for err in errors:
                    error_messages.append(f"{field}: {err}")
            error_string = " | ".join(error_messages)

            return Response(
                {
                    "status": 400,
                    "message": error_string,  # errors as string
                    "data": serializer.errors,  # keep full details if needed
                },
                status=400,
            )
            # return Response(
            #     {"status": 400, "message": "Validation error", "data": serializer.errors},
            #     status=400,
            # )
class ReplaceDeviceAPIView(APIView):
    def post(self, request):
        serializer = ReplaceDeviceSerializer(data=request.data)

        # validate first
        if not serializer.is_valid():
            return Response(
                {"status": 400, "message": "Validation error", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        customer_id = data["customer_id"]
        

        # check if customer exists
        customer = Customer.objects.filter(id=customer_id).first()
        print(customer)
        if not customer:
            return Response(
                {"status": 404, "message": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # check if old device exists
        old_device = Device.objects.filter(customer=customer, device_id=data["delete_device_id"]).first()
        if not old_device:
            return Response(
                {"status": 404, "message": "Old device not found", "data": None},
                status=status.HTTP_404_NOT_FOUND
            )
        #  Delete old device
        old_device.delete()

        # register new device
        new_device = Device.objects.create(
            customer=customer,
            device_id=data["device_id"],
            device_name=data["device_name"],
            device_model=data["device_model"],
            device_type=data["device_type"],
            ip_address=request.META.get("REMOTE_ADDR"),
            last_login=timezone.now(),
            status="active"
        )

        # generate JWT tokens
        refresh = RefreshToken.for_user(customer)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
    #return device_check_after_login(request, customer, access_token, refresh_token)
        # prepare response
        # response = Response(
        #     {
        #         "status": 200,
        #         "message": "Device replaced and logged in successfully",
        #         "data": {
        #             "old_device_id": old_device.device_id,
        #             "new_device_id": new_device.device_id,
        #             "device_name": new_device.device_name,
        #             "device_model": new_device.device_model,
        #             "device_type": new_device.device_type,
        #             "last_login": new_device.last_login.strftime("%Y-%m-%d %H:%M:%S"),
        #             "access_token": access_token
        #         },
               
        #     },
        #     status=status.HTTP_200_OK
        # )

        # ✅ Define serializer once so it’s available in all cases
        customer_serializer = CustomerSerializer(customer)
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
    


from .serializers import CustomerSerializer
from rest_framework_simplejwt.exceptions import TokenError
class VerifyAuthToken(APIView):
    def get(self, request):
        token = request.COOKIES.get("JWT_TOKEN")
        if not token:
            return Response({"status": 401, "message": "Unauthorised"}, status=401)

        try:
            refresh = RefreshToken(token)
            user_id = refresh["user_id"]   # extract claim

            # fetch customer
            customer = Customer.objects.filter(id=user_id).first()
            if not customer:
                return Response(
                    {"status": 404, "message": "Customer not found"},
                    status=404,
                )

            serializer = CustomerSerializer(customer)

            return Response(
                {
                    "status": 200,
                    "message": "Token valid",
                    "data": serializer.data,
                },
                status=200,
            )
        except TokenError:
            return Response(
                {"status": 401, "message": "Token invalid or expired"},
                status=401,
            )
        

class CustomerProfilesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user  # comes from JWT
        if not customer or not isinstance(customer, Customer):
            return Response({"status": 404, "message": "Customer not found"}, status=404)

        serializer = CustomerSerializer(customer)
        return Response({"status": 200, "message": "Success", "data": serializer.data})
    
class CreateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]  # JWT from cookie will set request.user

    def post(self, request):
        customer = request.user  # comes from JWT
        if not customer:
            return Response(
                {"status": 404, "message": "Customer not found"},
                status=404
            )

        data = {
            "customer": customer.id,  # pass ID to serializer
            "profile_name": request.data.get("profile_name", "New Profile"),
            "profile_type": request.data.get("profile_type", "adult"),
            "avatar_url": request.data.get("avatar_url"),
        }

        serializer = ProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save(customer=customer)  # ensure FK is bound correctly
            return Response(
                {"status": 200, "message": "Profile created", "data": serializer.data},
                status=200
            )

        return Response(
            {"status": 400, "message": "Validation failed", "errors": serializer.errors},
            status=400
        )



class ProfileDetailByCodeAPIView(APIView):
    def get(self, request, profile_code):
        profile = Profile.objects.filter(profile_code=profile_code).first()
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)
        
        profile_data = ProfileSerializer(profile).data
        customer_data = CustomerSerializer(profile.customer).data

        return Response({
            "status": 200,
            "message": "Success",
            "data": {
                "profile": profile_data,
                "customer": customer_data
            }
        })
    


    
# ---------------------------
# Edit a single profile
# ---------------------------
class EditProfileAPIView(APIView):
    def post(self, request, profile_id):
        profile = Profile.objects.filter(id=profile_id).first()
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)
        
        # Get data from request or fallback to existing values
        profile_name = request.data.get("profile_name", profile.profile_name)
        profile_type = request.data.get("profile_type", profile.profile_type)
      
        avatar_url = request.data.get("avatar_url")  # select from predefined list

        # Update fields
        profile.profile_name = profile_name
        profile.profile_type = profile_type

        # Update avatar: priority to uploaded file, then avatar_url, else keep existing
       
        profile.avatar_url = avatar_url
        # else: keep existing avatar (can be null)

        profile.save()

        serializer = ProfileSerializer(profile)
        return Response({
            "status": 200,
            "message": "Profile updated",
            "data": serializer.data
        })



# ---------------------------
# Delete a single profile
# ---------------------------
class DeleteProfileAPIView(APIView):
    def delete(self, request, profile_id):
        profile = Profile.objects.filter(id=profile_id).first()
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)
        profile.delete()
        return Response({"status": 200, "message": "Profile deleted"})


# ---------------------------
# Delete all profiles of a customer
# ---------------------------
class DeleteAllProfilesAPIView(APIView):
    def delete(self, request, customer_id):
        customer = Customer.objects.filter(id=customer_id).first()
        if not customer:
            return Response({"status": 404, "message": "Customer not found"}, status=404)

        profiles = Profile.objects.filter(customer=customer)
        deleted_count = profiles.count()
        profiles.delete()

        return Response({
            "status": 200,
            "message": f"Deleted {deleted_count} profiles for customer {customer.name}"
        })
    

class AvailableAvatarsAPIView(APIView):
    def get(self, request):
        avatars_path = os.path.join(settings.MEDIA_ROOT, 'avatars')
        avatar_files = []
        if os.path.exists(avatars_path):
            avatar_files = [
                f"http://{request.get_host()}/media/avatars/{file_name}"
                for file_name in os.listdir(avatars_path)
                if os.path.isfile(os.path.join(avatars_path, file_name))
            ]

        return Response({
            "status": 200,
            "message": "Success",
            "data": avatar_files
        })