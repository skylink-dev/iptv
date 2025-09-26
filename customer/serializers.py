from rest_framework import serializers
from .models import Customer, Device , Profile , Avatar # make sure Customer model exists in customer/models.py


from django.conf import settings

from rest_framework import serializers
from .models import Profile, Avatar, WatchHistory, Favorite
from iptvengine.models import Channel
from iptvengine.serializers import ChannelSerializer

class AvatarSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Avatar
        fields = ["id", "image", "uploaded_at", "is_active"]

class ProfileSerializer(serializers.ModelSerializer):
    # Read-only field for returning avatar URL
    avatar = serializers.SerializerMethodField()

    # Write-only field for updating avatar via ID
    avatar_id = serializers.PrimaryKeyRelatedField(
        source='avatar',  # maps avatar_id to avatar FK
        queryset=Avatar.objects.filter(is_active=True),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Profile
        fields = ["id", "profile_name", "profile_type", "avatar", "avatar_id", "profile_code"]
        read_only_fields = ["profile_code"]

    def get_avatar(self, obj):
        if obj.avatar and obj.avatar.image:
            request = self.context.get('request')  # Must pass request in context
            return request.build_absolute_uri(obj.avatar.image.url) if request else obj.avatar.image.url
        return None

    def validate(self, data):
        """
        Ensure profile_name is unique per customer.
        """
        request = self.context.get("request")
        customer = getattr(request.user, "customer", None) if request else None

        # Allow passing customer explicitly in request data if not from request.user
        if not customer:
            customer = data.get("customer") or getattr(self.instance, "customer", None)

        profile_name = data.get("profile_name") or getattr(self.instance, "profile_name", None)

        if customer and profile_name:
            qs = Profile.objects.filter(customer=customer, profile_name=profile_name)

            # Exclude the current instance when updating
            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                raise serializers.ValidationError(
                    {"profile_name": "This profile name already exists for this customer."}
                )

        return data



class CustomerSerializer(serializers.ModelSerializer):
    # Nest the profiles serializer
    profiles = ProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            "customer_id",
            "name",
            "email",
            "phone",
            "address",
            "account_status",
            "billing_status",
            "subscription_plan",
            "subscription_start",
            "subscription_end",
            "next_due_date",
            "city",
            "state",
            "country",
            "profiles"  # now full details
        ]



# Your existing serializers
class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15,
        required=False,
        allow_blank=True,
        help_text="Enter phone number",
        initial="9876543210"
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Enter email",
        initial="test@example.com"
    )
    code = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Enter customer code",
        initial="CUSTOMER123"
    )


from rest_framework import serializers

class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15,
        required=False,
        allow_blank=True,
        help_text="Enter phone number",
        initial="9876543210"
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Enter email",
        initial="test@example.com"
    )
    code = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Enter customer code",
        initial="CUSTOMER123"
    )
    otp = serializers.CharField(
        max_length=6,
        required=True,
        help_text="Enter OTP received",
        initial="123456"
    )

    # ✅ new fields for device info
    device_id = serializers.CharField(required=True, help_text="Unique device ID")
    device_name = serializers.CharField(required=True, help_text="Device name")
    device_model = serializers.CharField(required=True, help_text="Device model")
    device_type = serializers.CharField(required=True, help_text="Device type (MOBILE/TV/etc)")

    def validate(self, attrs):
        phone = attrs.get("phone")
        email = attrs.get("email")
        code = attrs.get("code")
        device_id=attrs.get("device_id")
        device_name=attrs.get("device_name")
        device_model=attrs.get("device_model")
        device_type=attrs.get("device_type")


        # 🔹 Rule 1: One identifier must exist
        if not (phone or email or code):
            raise serializers.ValidationError(
                "Either phone, email, or code is required."
            )
        if not (device_name and device_model and device_type or device_id):
            raise serializers.ValidationError(
                "All device details (device_id, device_name, device_model, device_type) are required."
            )


        # 🔹 Rule 2: OTP is already required, so no need to check again

        # 🔹 Rule 3: Device details must be provided (serializer ensures required=True)
        # but if you want extra strictness:

        required_fields = ["device_id", "device_name", "device_model", "device_type"]
        missing = [f for f in required_fields if not attrs.get(f)]
        if missing:
            raise serializers.ValidationError(
                {f: "This field is required." for f in missing}
            )
            

        return attrs



class ReplaceDeviceSerializer(serializers.Serializer):
    delete_device_id = serializers.CharField(required=True, help_text="Device ID to remove")
    device_id = serializers.CharField(required=True, help_text="New device unique ID")
    device_name = serializers.CharField(required=True, help_text="New device name")
    device_model = serializers.CharField(required=True, help_text="New device model")
    device_type = serializers.CharField(required=True, help_text="New device type (MOBILE/TV/etc)")
    customer_id = serializers.IntegerField(required=True)



class AddWatchHistorySerializer(serializers.Serializer):
    channel_id = serializers.IntegerField(required=True)

    def validate_channel_id(self, value):
        if not Channel.objects.filter(id=value).exists():
            raise serializers.ValidationError("Channel not found")
        return value



class WatchHistorySerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(read_only=True)  # nest full channel details
    profile_code = serializers.CharField(source="profile.profile_code", read_only=True)
    profile_name = serializers.CharField(source="profile.profile_name", read_only=True)

    class Meta:
        model = WatchHistory
        fields = [
            "profile_code",
            "profile_name",
            "channel",
            "updated_at"
        ]


        
class FavoriteSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(read_only=True)
    profile_code = serializers.CharField(source="profile.profile_code", read_only=True)
    profile_name = serializers.CharField(source="profile.profile_name", read_only=True)

    class Meta:
        model = Favorite
        fields = [
            "id",
            "profile_code",
            "profile_name",
            "channel",
            "updated_at",
        ]