# customer/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    ReplaceDeviceSerializer,
    ProfileSerializer,
    CustomerSerializer,
    AddWatchHistorySerializer, 
    WatchHistorySerializer, FavoriteSerializer
)
from .models import Device, Customer, Profile, Avatar,WatchHistory,Favorite

from utils.sms_utils import send_verification_sms, verify_sms_otp
from utils.email_utils import send_verification_email, verify_email_otp
from utils.device_verified_utils import device_check_after_login, get_current_profile, get_weather

import os
from launcher.models import LauncherWallpaper
from launcher.serializers import LauncherWallpaperSerializer

from iptvengine.models import Channel



class SendOTPAPIView(APIView):
    permission_classes = [AllowAny]

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
        serializer = OTPRequestSerializer(data=request.data or {})
        if not serializer.is_valid():
            return Response(
                {"status": 400, "message": "Validation error", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data.get("phone")
        email = serializer.validated_data.get("email")
        code = serializer.validated_data.get("code")

        if phone:
            send_verification_sms(phone)
            return Response({"status": 200, "message": f"OTP sent to phone {phone}"}, status=status.HTTP_200_OK)

        if email:
            send_verification_email(email)
            return Response({"status": 200, "message": f"OTP sent to email {email}"}, status=status.HTTP_200_OK)

        if code:
            try:
                customer = Customer.objects.get(iptv_activation_code=code)
            except Customer.DoesNotExist:
                return Response({"status": 404, "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            if customer.phone:
                send_verification_sms(customer.phone)
                return Response({"status": 200, "message": f"OTP sent to phone {customer.phone}"}, status=status.HTTP_200_OK)
            if customer.email:
                send_verification_email(customer.email)
                return Response({"status": 200, "message": f"OTP sent to email {customer.email}"}, status=status.HTTP_200_OK)

            return Response({"status": 400, "message": "No phone/email found for this code"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": 400, "message": "No contact provided"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data or {})
        if not serializer.is_valid():
            # Build single-line error message + return full errors
            error_messages = []
            for field, errors in serializer.errors.items():
                for err in errors:
                    error_messages.append(f"{field}: {err}")
            error_string = " | ".join(error_messages)
            return Response(
                {"status": 400, "message": error_string, "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data.get("phone")
        email = serializer.validated_data.get("email")
        code = serializer.validated_data.get("code")
        otp = serializer.validated_data.get("otp")

        customer = None
        result = None
        otp_failed_status = 400

        # Phone flow
        if phone:
            customer = Customer.objects.filter(phone=phone).first()
            result = verify_sms_otp(phone, otp)

        # Email flow
        elif email:
            customer = Customer.objects.filter(email=email).first()
            result = verify_email_otp(email, otp)

        # Code flow
        elif code:
            customer = Customer.objects.filter(iptv_activation_code=code).first()
            if not customer:
                return Response({"status": 404, "message": "Customer not found", "data": None}, status=status.HTTP_404_NOT_FOUND)

            if customer.phone:
                result = verify_sms_otp(customer.phone, otp)
            elif customer.email:
                result = verify_email_otp(customer.email, otp)
            else:
                return Response({"status": 400, "message": "No contact info found", "data": None}, status=status.HTTP_400_BAD_REQUEST)

        # Customer must exist
        if not customer:
            return Response({"status": 404, "message": "Customer not found", "data": None}, status=status.HTTP_404_NOT_FOUND)

        # OTP verification result
        if not result or not result.get("success"):
            return Response({"status": otp_failed_status, "message": result.get("message", "OTP failed"), "data": None}, status=otp_failed_status)

        # OTP is valid: generate tokens and handle device logic
        refresh = RefreshToken.for_user(customer)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return device_check_after_login(request, customer, access_token, refresh_token)


class ReplaceDeviceAPIView(APIView):
    permission_classes = [AllowAny]  # Keep public if you expect caller to be unauthenticated (depends on your flow)

    def post(self, request):
        serializer = ReplaceDeviceSerializer(data=request.data or {})
        if not serializer.is_valid():
            return Response({"status": 400, "message": "Validation error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer_id = data.get("customer_id")
        if not customer_id:
            return Response({"status": 400, "message": "customer_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.filter(id=customer_id).first()
        if not customer:
            return Response({"status": 404, "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        # check old device
        old_device = Device.objects.filter(customer=customer, device_id=data.get("delete_device_id")).first()
        if not old_device:
            return Response({"status": 404, "message": "Old device not found", "data": None}, status=status.HTTP_404_NOT_FOUND)

        # delete old device
        old_device.delete()

        # create new device
        new_device = Device.objects.create(
            customer=customer,
            device_id=data.get("device_id"),
            device_name=data.get("device_name"),
            device_model=data.get("device_model"),
            device_type=data.get("device_type"),
            ip_address=request.META.get("REMOTE_ADDR"),
            last_login=timezone.now(),
            status="active",
        )

        # generate tokens
        refresh = RefreshToken.for_user(customer)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        customer_serializer = CustomerSerializer(customer)
        response = Response(
            {
                "status": 200,
                "message": "Device replaced and logged in successfully",
                "data": {
                    **customer_serializer.data,
                    "access_token": access_token,
                },
            },
            status=status.HTTP_200_OK,
        )

        # set cookie (consider httponly=True in production)
        response.set_cookie(
            key="JWT_TOKEN",
            value=access_token,
            httponly=False,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7,
        )

        return response


class VerifyAuthToken(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.COOKIES.get("JWT_TOKEN")
        if not token:
            return Response({"status": 401, "message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            access_token = AccessToken(token)
            user_id = access_token.get("user_id")
            if not user_id:
                return Response({"status": 401, "message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

            customer = Customer.objects.filter(id=user_id).first()
            if not customer:
                return Response({"status": 404, "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            # serialize customer
            customer_data = CustomerSerializer(customer, context={"request": request}).data

            # serialize wallpapers (only active)
            wallpapers = LauncherWallpaper.objects.filter(is_active=True).order_by("order")
            wallpapers_data = LauncherWallpaperSerializer(wallpapers, many=True, context={"request": request}).data

            # Inside API view
            weather_data = get_weather(request)
            return Response(
                {
                    "status": 200,
                    "message": "Token valid",
                    "data": {
                        "customer": customer_data,
                        "wallpapers": wallpapers_data,
                         "weather": weather_data
                    }
                },
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response({"status": 401, "message": "Token invalid or expired"}, status=status.HTTP_401_UNAUTHORIZED)


class CustomerProfilesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user
        if not isinstance(customer, Customer):
            return Response(
                {"status": 401, "message": "Invalid user", "data": None},
                status=status.HTTP_401_UNAUTHORIZED
            )

        profiles = Profile.objects.filter(customer=customer)

        # Pass request in context to generate full avatar URL
        serializer = ProfileSerializer(profiles, many=True, context={'request': request})

        return Response(
            {"status": 200, "message": "Success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

class CreateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer = request.user
        if not isinstance(customer, Customer):
            return Response({"status": 401, "message": "Invalid customer"}, status=401)

        avatar_id = request.data.get("avatar")
        avatar_instance = None
        if avatar_id:
            try:
                avatar_instance = Avatar.objects.get(id=avatar_id, is_active=True)
            except Avatar.DoesNotExist:
                return Response({"status": 400, "message": "Invalid avatar ID"})

        profile = Profile.objects.create(
            customer=customer,
            profile_name=request.data.get("profile_name", "New Profile"),
            profile_type=request.data.get("profile_type", "adult"),
            avatar=avatar_instance
        )

        serializer = ProfileSerializer(profile)
        return Response({"status": 200, "message": "Profile created", "data": serializer.data})


class ProfileDetailByCodeAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, profile_code):
        profile = Profile.objects.filter(profile_code=profile_code).first()
        if not profile:
            return Response(
                {"status": 404, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Pass request in context to generate full avatar URL
        profile_data = ProfileSerializer(profile, context={'request': request}).data
        customer_data = CustomerSerializer(profile.customer, context={'request': request}).data

        return Response(
            {"status": 200, "message": "Success", "data": {"profile": profile_data, "customer": customer_data}},
            status=status.HTTP_200_OK
        )
    
class EditProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        profile_id = request.data.get("profile_id")
        if not profile_id:
            return Response({"status": 400, "message": "Profile ID is required", "data": None}, status=400)

        profile = Profile.objects.filter(id=profile_id).first()
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        # Prepare data
        data = {
            "profile_name": request.data.get("profile_name", profile.profile_name),
            "profile_type": request.data.get("profile_type", profile.profile_type),
        }

        # Handle avatar by ID
        avatar_id = request.data.get("avatar_id")
    
        if avatar_id:
            avatar_instance = Avatar.objects.filter(id=avatar_id).first()
            if not avatar_instance:
                return Response({"status": 400, "message": "Invalid avatar ID", "data": None}, status=400)
            data["avatar"] = avatar_instance  # Pass instance, not ID
        print(data)
        # Pass context for validation
        serializer = ProfileSerializer(profile, data=data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({"status": 200, "message": "Profile updated", "data": serializer.data})
        else:
            error_messages = [f"{f}: {e[0]}" for f, e in serializer.errors.items()]
            return Response({"status": 400, "message": " | ".join(error_messages), "data": serializer.errors}, status=400)





class DeleteProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, profile_id):
        customer = request.user
        if not isinstance(customer, Customer):
            return Response({"status": 401, "message": "Invalid customer", "data": None}, status=status.HTTP_401_UNAUTHORIZED)

        profile = Profile.objects.filter(id=profile_id, customer=customer).first()
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        profile.delete()
        return Response({"status": 200, "message": "Profile deleted"}, status=status.HTTP_200_OK)


class DeleteAllProfilesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        customer = request.user
        if not isinstance(customer, Customer):
            return Response({"status": 401, "message": "Invalid customer", "data": None}, status=status.HTTP_401_UNAUTHORIZED)

        profiles = Profile.objects.filter(customer=customer)
        deleted_count = profiles.count()
        profiles.delete()
        return Response({"status": 200, "message": f"Deleted {deleted_count} profiles for customer {getattr(customer, 'name', customer.id)}"}, status=status.HTTP_200_OK)


class AvailableAvatarsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Fetch all active avatars
        avatars = Avatar.objects.filter(is_active=True).order_by("-uploaded_at")

        # Create list of dictionaries with id and url
        avatar_files = [{"id": avatar.id, "url": request.build_absolute_uri(avatar.image.url)} for avatar in avatars]

        return Response({
            "status": 200,
            "message": "Success",
            "data": avatar_files
        }, status=status.HTTP_200_OK)
    
class AddWatchHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer = request.user
        profile = get_current_profile(request, customer)

        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        channel_id = request.data.get("channel_id")
        if not channel_id:
            return Response({"status": 400, "message": "channel_id is required"}, status=400)

        channel = Channel.objects.filter(id=channel_id).first()
        if not channel:
            return Response({"status": 404, "message": "Channel not found"}, status=404)

        # Insert or update watch history
        history, created = WatchHistory.objects.update_or_create(
            customer=customer,
            profile=profile,
            channel=channel,
            defaults={"updated_at": timezone.now()}
        )

        # Keep only latest 10
        history_qs = WatchHistory.objects.filter(profile=profile).order_by("-updated_at")
        if history_qs.count() > 10:
            for old in history_qs[10:]:
                old.delete()

        return Response({"status": 200, "message": "Watch history updated"})
class GetWatchHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user
        profile = get_current_profile(request, customer)

        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        # latest first
        history_qs = WatchHistory.objects.filter(profile=profile).select_related("channel").order_by("-updated_at")[:10]

        serializer = WatchHistorySerializer(history_qs, many=True, context={"request": request})

        return Response({"status": 200, "data": serializer.data})


class DeleteAllWatchHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        customer = request.user
        profile = get_current_profile(request, customer)

        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        deleted_count, _ = WatchHistory.objects.filter(profile=profile).delete()

        return Response({
            "status": 200,
            "message": f"All watch history deleted ({deleted_count} items)"
        })
    

    
# views.py
class DeleteWatchHistoryItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        customer = request.user
        profile = get_current_profile(request, customer)

        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        watch_item = WatchHistory.objects.filter(profile=profile, id=pk).first()

        if not watch_item:
            return Response({"status": 404, "message": "Watch history item not found"}, status=404)

        watch_item.delete()
        return Response({
            "status": 200,
            "message": f"Watch history item {pk} removed"
        })

#---------------------------------


# Add Favorite
class AddFavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer = request.user
        profile = get_current_profile(request, customer)
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        channel_id = request.data.get("channel_id")
        if not channel_id:
            return Response({"status": 400, "message": "channel_id is required"}, status=400)

        channel = Channel.objects.filter(id=channel_id).first()
        if not channel:
            return Response({"status": 404, "message": "Channel not found"}, status=404)

        favorite, created = Favorite.objects.update_or_create(
            customer=customer,
            profile=profile,
            channel=channel,
            defaults={"updated_at": timezone.now()}
        )

        return Response({"status": 200, "message": "Favorite updated"})


# List Favorites
class GetFavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user
        profile = get_current_profile(request, customer)
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        favorites_qs = Favorite.objects.filter(profile=profile).select_related("channel").order_by("-updated_at")[:10]
        serializer = FavoriteSerializer(favorites_qs, many=True, context={"request": request})

        return Response({"status": 200, "data": serializer.data})


# Delete Single Favorite
class DeleteFavoriteItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        customer = request.user
        profile = get_current_profile(request, customer)
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        fav_item = Favorite.objects.filter(profile=profile, id=pk).first()
        if not fav_item:
            return Response({"status": 404, "message": "Favorite item not found"}, status=404)

        fav_item.delete()
        return Response({"status": 200, "message": f"Favorite item removed"})


# Delete All Favorites
class DeleteAllFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        customer = request.user
        profile = get_current_profile(request, customer)
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        deleted_count, _ = Favorite.objects.filter(profile=profile).delete()
        return Response({"status": 200, "message": f"All favorites deleted ({deleted_count} items)"})