from django.urls import path
from .views import DashboardAPIView, LauncherChannelSearchAPIView

urlpatterns = [
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard-api"),
    path('search/', LauncherChannelSearchAPIView.as_view(), name='launcher-channel-search'),
]
