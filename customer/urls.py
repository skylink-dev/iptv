from django.urls import path, include
from .views import otp_login_view, customer_api_root
from .api_views import SendOTPAPIView, VerifyOTPAPIView, ReplaceDeviceAPIView, VerifyAuthToken, CustomerProfilesAPIView, CreateProfileAPIView, ProfileDetailByCodeAPIView, EditProfileAPIView,    DeleteProfileAPIView,    DeleteAllProfilesAPIView , AvailableAvatarsAPIView, AddWatchHistoryAPIView, GetWatchHistoryAPIView, DeleteAllWatchHistoryAPIView,  DeleteWatchHistoryItemAPIView, AddFavoriteAPIView, GetFavoriteAPIView, DeleteFavoriteItemAPIView, DeleteAllFavoritesAPIView
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
    path('profiles/create/', CreateProfileAPIView.as_view(), name='create-profile'),
    path('profile/<str:profile_code>/', ProfileDetailByCodeAPIView.as_view(), name='profile-detail-code'),

    path('profiles/edit/', EditProfileAPIView.as_view(), name='edit-profile'),
    path('profiles/<int:profile_id>/delete/', DeleteProfileAPIView.as_view(), name='delete-profile'),
    path('profiles/delete-all/', DeleteAllProfilesAPIView.as_view(), name='delete-all-profiles'),
    
    # Available avatars
    path('avatars_list/', AvailableAvatarsAPIView.as_view(), name='available-avatars'),


    # Replace device API
     path("device/replace/", ReplaceDeviceAPIView.as_view(), name="replace-device"),

    # Include router URLs for DeviceViewSet
    path("", include(router.urls)),



    # watch list
    path("watch-history/add/", AddWatchHistoryAPIView.as_view(), name="add-watch-history"),
    path("watch-history/", GetWatchHistoryAPIView.as_view(), name="get-watch-history"),
    path("watch-history/delete-all/", DeleteAllWatchHistoryAPIView.as_view(), name="delete-all-watch-history"),
    path("watch-history/delete/<int:pk>/", DeleteWatchHistoryItemAPIView.as_view(), name="delete-watch-history-item"),

    #favorites
    path("favorites/add/", AddFavoriteAPIView.as_view(), name="add-favorite"),
    path("favorites/", GetFavoriteAPIView.as_view(), name="get-favorites"),
    path("favorites/delete/<int:pk>/", DeleteFavoriteItemAPIView.as_view(), name="delete-favorite-item"),
    path("favorites/delete-all/", DeleteAllFavoritesAPIView.as_view(), name="delete-all-favorites"),

]
