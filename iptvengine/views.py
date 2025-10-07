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


from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework import status



class GetChannelEPGAPIView(APIView):
    """
    Fetches the EPG JSON from remote server and returns it directly.
    """

    def get(self, request, channel_id):
        channel = Channel.objects.filter(channel_id=channel_id).first()
        if not channel:
            return Response({"detail": "Channel not found"}, status=404)

        epg_url = f"http://172.19.0.1/epg/{channel.channel_id}.json"
        headers = {
            "d-uuid": "5b0c8177-c484-4b85-960d-48d3238abb05",
            "d-crypt": "2",
            "d-token": "7f3b65ad1da6cfb8844c7958f416b051",
            "d-version": "1.11.08",
        }

        try:
            response = requests.get(epg_url, headers=headers, timeout=10)

            if response.status_code == 404:
                return Response({"message": "EPG not found on remote server"}, status=404)
            elif not response.ok:
                return Response({"message": f"Remote server returned {response.status_code}"}, status=502)

            epg_data = response.json()

            # FIX: if epg_data is a list, return directly
            if isinstance(epg_data, list):
                return Response(epg_data)

            # fallback for unexpected formats
            return Response({"message": "Unexpected EPG format"}, status=500)

        except requests.exceptions.RequestException as e:
            return Response({"message": str(e)}, status=502)