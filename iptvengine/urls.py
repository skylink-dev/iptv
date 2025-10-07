from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TariffViewSet, ChannelViewSet, ChannelGroupViewSet,
    LanguageViewSet, CategoryViewSet, RadioViewSet, GetChannelEPGAPIView
)

router = DefaultRouter()
router.register(r'languages', LanguageViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'channels', ChannelViewSet)
router.register(r'channel-groups', ChannelGroupViewSet)
router.register(r'tariffs', TariffViewSet)

router.register(r'radios', RadioViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("channel/<int:channel_id>/epg/", GetChannelEPGAPIView.as_view(), name="channel-epg"),
]
