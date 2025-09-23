from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Customer, Device, VerificationCode, Setting


class DeviceInline(admin.TabularInline):
    model = Device
    extra = 1
    fields = ("device_name", "device_model", "device_id", "device_type",  "ip_address", "last_login", "status")
    readonly_fields = ("last_login",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "customer_id", "name", "email", "phone",
        "partner", "subscription_plan",
        "account_status", "billing_status", "next_due_date",
        "action_buttons",   # ✅ renamed
    )
    list_filter = ("account_status", "billing_status", "partner", "subscription_plan", "city", "state", "country")
    search_fields = ("customer_id", "name", "email", "phone", "username")
    ordering = ("-created_at",)
    readonly_fields = ( "created_at", "updated_at")
    inlines = [DeviceInline]

    fieldsets = (
        ("Basic Information", {
            "fields": ("customer_id", "partner", "name", "email", "phone", "address")
        }),
        ("IPTV Subscription", {
            "fields": ("subscription_plan", "iptv_activation_code", "subscription_start", "subscription_end",
                       "account_status", "billing_status", "next_due_date")
        }),
        ("Login Credentials", {
            "fields": ("username", "password")
        }),
        ("Location", {
            "fields": ("city", "state", "country", "latitude", "longitude")
        }),
        ("System Info", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def action_buttons(self, obj):
        """Custom Edit/Delete buttons in list view"""
        edit_url = reverse("admin:customer_customer_change", args=[obj.pk])
        delete_url = reverse("admin:customer_customer_delete", args=[obj.pk])

        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Edit</a> '
            '<a class="btn btn-sm btn-danger" href="{}">Delete</a>',
            edit_url, delete_url
        )

    action_buttons.short_description = "Actions"
    action_buttons.allow_tags = True


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "customer", "device_name", "device_model", "device_type", "device_id",
        "ip_address", "status", "last_login", "created_at", "action_buttons"
    )
    list_filter = ("status", "customer")
    search_fields = ("device_name", "device_id", "ip_address", "customer__customer_id")
    ordering = ("-created_at",)

    def action_buttons(self, obj):
        """Custom Edit/Delete buttons in list view"""
        edit_url = reverse("admin:customer_device_change", args=[obj.pk])
        delete_url = reverse("admin:customer_device_change", args=[obj.pk])

        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Edit</a> '
            '<a class="btn btn-sm btn-danger" href="{}">Delete</a>',
            edit_url, delete_url
        )

    action_buttons.short_description = "Actions"
    action_buttons.allow_tags = True



@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "code", "timestamp", "is_valid")
    search_fields = ("phone_number", "code")
    list_filter = ("timestamp",)


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ("max_devices", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        # Allow add only if no Setting exists
        if Setting.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the only settings record
        return False