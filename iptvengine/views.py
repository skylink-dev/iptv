from rest_framework import viewsets, filters
from .models import (
    Tariff, Channel, ChannelGroup,
    Language, Category, Radio
)
from .serializers import (
    TariffSerializer, ChannelSerializer,
    ChannelGroupSerializer, LanguageSerializer, CategorySerializer,
    RadioSerializer
)


# ------------------------------
# Language & Category
# ------------------------------
class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


# ------------------------------
# Channel & ChannelGroup
# ------------------------------
class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'channel_id']


class ChannelGroupViewSet(viewsets.ModelViewSet):
    queryset = ChannelGroup.objects.all()
    serializer_class = ChannelGroupSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


# ------------------------------
# Tariff
# ------------------------------
class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']





# ------------------------------
# Radio
# ------------------------------
class RadioViewSet(viewsets.ModelViewSet):
    queryset = Radio.objects.all()
    serializer_class = RadioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'language__name']
