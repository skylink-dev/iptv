from django.urls import path, include
from .views import otp_login_view, customer_api_root
from .api_views import SendOTPAPIView, VerifyOTPAPIView, DeviceViewSet, ReplaceDeviceAPIView
from rest_framework.routers import DefaultRouter

# Router for ViewSets
router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename="device")

urlpatterns = [
    # OTP views
    path("otp-login/", otp_login_view, name="otp-login"),
    path("send-otp/", SendOTPAPIView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),

    # Replace device API
    path("devices/replace/", ReplaceDeviceAPIView.as_view(), name="replace-device"),

    # Include router URLs for DeviceViewSet
    path("", include(router.urls)),
]
