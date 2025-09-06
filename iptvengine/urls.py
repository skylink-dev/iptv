from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TariffViewSet, ChannelViewSet, ChannelGroupViewSet,
    LanguageViewSet, CategoryViewSet, RadioViewSet
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
]
