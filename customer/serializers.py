from rest_framework import serializers
from .models import Customer, Device , Profile  # make sure Customer model exists in customer/models.py



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "profile_name", "profile_type", "avatar_url", "profile_code"]

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



  