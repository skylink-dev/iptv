from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from customer.models import Profile
from launcher.models import Category
from launcher.serializers import CategorySerializer


from iptvengine.models import Channel, Radio
from iptvengine.serializers import ChannelSerializer,RadioSerializer

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get profile_code from headers
        profile_code = request.headers.get("Current-Profile-Code")  # use a custom header
        profile = None
        if profile_code:
            profile = Profile.objects.filter(profile_code=profile_code, customer=request.user).first()
        
        if not profile:
            return Response({"status": 404, "message": "Profile not found"}, status=404)

        categories = Category.objects.all()

        # Pass profile in serializer context
        serializer = CategorySerializer(categories, many=True, context={"request": request, "profile": profile})

        return Response({
            "status": 200,
            "message": "Success",
            "data": {"categories": serializer.data}
        })
class LauncherChannelSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get search parameters
        search_text = request.query_params.get("search", "")
        channel_type = request.query_params.get("type", "").upper()  # LIVETV or FM
        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("size", 15))

        paginator = PageNumberPagination()
        paginator.page_size = size

        if channel_type == "LIVETV":
            queryset = Channel.objects.filter(status="ACTIVE")
            if search_text:
                queryset = queryset.filter(Q(name__icontains=search_text) | Q(description__icontains=search_text))
            paginated_qs = paginator.paginate_queryset(queryset, request)
            serializer = ChannelSerializer(paginated_qs, many=True, context={"request": request})

        elif channel_type == "FM":  # Radio search
            queryset = Radio.objects.all()
            if search_text:
                queryset = queryset.filter(Q(name__icontains=search_text) | Q(language__name__icontains=search_text))
            paginated_qs = paginator.paginate_queryset(queryset, request)
            serializer = RadioSerializer(paginated_qs, many=True, context={"request": request})

        else:
            return Response({"status": 400, "message": "Invalid type. Use LIVETV or FM."})

        return paginator.get_paginated_response(serializer.data)