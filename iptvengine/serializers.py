from rest_framework import serializers
from .models import (
    Tariff, Channel, ChannelGroup,
    Language, Category, Radio,
    SourceHeader, LicenseHeaderItem
)

# ------------------------------
# Language Serializer
# ------------------------------
class LanguageSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Language
        fields = ("id", "name", "image_url", "display_order", "created_at")
        read_only_fields = ("created_at",)


# ------------------------------
# Category Serializer
# ------------------------------
class CategorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("created_at",)


# ------------------------------
# Source & License Header Serializers
# ------------------------------
class SourceHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceHeader
        fields = ("id", "key", "value")


class LicenseHeaderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseHeaderItem
        fields = ("id", "key", "value")


# ------------------------------
# Channel Serializer
# ------------------------------
class ChannelSerializer(serializers.ModelSerializer):
    source_headers = serializers.SerializerMethodField()
    license_headers = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()  # override logo field

    class Meta:
        model = Channel
        fields = (
            "id", "channel_id", "name", "description", "is_payed", "price", "logo",
            "order", "favorite", "timeshift", "adult", "show_price",
            "ppv", "ppv_link", "drm_type", "status", 
            "category", "language", "source_url", "license_url",
            "source_headers", "license_headers"
        )
        read_only_fields = ("created_at",)

    def get_logo(self, obj):
        request = self.context.get("request")
        if obj.logo:
            # If logo is an ImageField, get its URL
            logo_url = obj.logo.url if hasattr(obj.logo, "url") else f"{settings.MEDIA_URL}{obj.logo}"
            if request:
                return request.build_absolute_uri(logo_url)
            return logo_url
        if obj.channel_id:
            fallback_url = f"http://172.19.0.1/static/tv/logos/{obj.channel_id}.png"
            return fallback_url
        return None


    def get_source_headers(self, obj):
        """
        Convert source headers list -> dict
        """
        headers = obj.source_headers.all()
        if not headers.exists():
            return None
        return {h.key: h.value for h in headers}

    def get_license_headers(self, obj):
        """
        Convert license headers list -> dict, return null if empty
        """
        headers = obj.license_headers.all()
        if not headers.exists():
            return None
        return {h.key: h.value for h in headers}

# ------------------------------
# Other Serializers
# ------------------------------
class ChannelGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelGroup
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")





class RadioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Radio
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
