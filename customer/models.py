from django.db import models
from django.utils import timezone
from iptvengine.models import Tariff 

from django.utils import timezone
from datetime import timedelta


class Customer(models.Model):
    customer_id = models.CharField(
        max_length=20, unique=True, db_index=True, blank=True
    )  # Will generate like CUST0001
    partner = models.ForeignKey(
        "partner.Partner",
        on_delete=models.CASCADE,
        related_name="customers",
        db_index=True,
        null=True,
        blank=True
    )

    # Basic Info
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True, blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, db_index=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    iptv_activation_code = models.CharField(max_length=200, blank=True, null=True)
    # IPTV specific
    subscription_plan = models.ForeignKey(
        Tariff,
        on_delete=models.SET_NULL,
        related_name="customers",
        blank=True,
        null=True,
        db_index=True
    )
    subscription_start = models.DateField(default=timezone.now, blank=True, null=True)
    subscription_end = models.DateField(blank=True, null=True)

    account_status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("suspended", "Suspended"),
            ("expired", "Expired"),
        ],
        default="inactive",
    )
    billing_status = models.CharField(
        max_length=20,
        choices=[
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
            ("overdue", "Overdue"),
        ],
        default="unpaid",
    )
    next_due_date = models.DateField(blank=True, null=True)

    # Login credentials (optional)
    username = models.CharField(max_length=150, unique=True, db_index=True, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    # Weather/location
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="India", blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # System
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            last = Customer.objects.all().order_by("-id").first()
            next_id = 1 if not last else last.id + 1
            self.customer_id = f"CUST{next_id:05d}"  # CUST00001 format
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_id} - {self.name or 'Unnamed'}"


class Device(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="devices"
    )
    device_name = models.CharField(max_length=100, blank=True, null=True)  # e.g., Mobile, TV, Laptop
    device_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_name or 'Device'} ({self.status})"




class VerificationCode(models.Model):
    phone_number = models.CharField(max_length=15, db_index=True, null=True, blank=True)
    email = models.EmailField(db_index=True, null=True, blank=True)
    code = models.CharField(max_length=6)
    timestamp = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        """Check if OTP is still valid (5 minutes)."""
        return timezone.now() <= self.timestamp + timedelta(minutes=30) # 30 minutes validity for testing

    def __str__(self):
        return f"{self.phone_number} - {self.code}"


# customer/models.py

class Setting(models.Model):
    max_devices = models.PositiveIntegerField(
        default=2,
        help_text="Maximum number of devices allowed per customer"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"Max Devices: {self.max_devices}"
