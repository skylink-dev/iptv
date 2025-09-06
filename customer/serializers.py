from rest_framework import serializers
from .models import Customer, Device   # make sure Customer model exists in customer/models.py


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"   # or list fields explicitly if you don’t want all

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



class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"