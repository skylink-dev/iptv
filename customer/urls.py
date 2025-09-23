from django.urls import path, include
from .views import otp_login_view, customer_api_root
from .api_views import SendOTPAPIView, VerifyOTPAPIView, ReplaceDeviceAPIView, VerifyAuthToken, CustomerProfilesAPIView, CreateProfileAPIView, ProfileDetailByCodeAPIView, EditProfileAPIView,    DeleteProfileAPIView,    DeleteAllProfilesAPIView , AvailableAvatarsAPIView
from rest_framework.routers import DefaultRouter

# Router for ViewSets
router = DefaultRouter()


urlpatterns = [


    # OTP views
    path("otp-login/", otp_login_view, name="otp-login"),
    path("send-otp/", SendOTPAPIView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("verify-auth-token/", VerifyAuthToken.as_view(), name="verify-auth-token"),

    # List all profiles of a customer
    path("profiles/", CustomerProfilesAPIView.as_view(), name="customer-profiles"),

    # Create new profile for a customer
    path('<int:customer_id>/profiles/create/', CreateProfileAPIView.as_view(), name='create-profile'),
    path('profile/<str:profile_code>/', ProfileDetailByCodeAPIView.as_view(), name='profile-detail-code'),

    path('profiles/<int:profile_id>/edit/', EditProfileAPIView.as_view(), name='edit-profile'),
    path('profiles/<int:profile_id>/delete/', DeleteProfileAPIView.as_view(), name='delete-profile'),
    path('<int:customer_id>/profiles/delete-all/', DeleteAllProfilesAPIView.as_view(), name='delete-all-profiles'),
    
    # Available avatars
    path('avatars_list/', AvailableAvatarsAPIView.as_view(), name='available-avatars'),


    # Replace device API
     path("device/replace/", ReplaceDeviceAPIView.as_view(), name="replace-device"),

    # Include router URLs for DeviceViewSet
    path("", include(router.urls)),
]
