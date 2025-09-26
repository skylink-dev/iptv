from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Customer, Device, VerificationCode, Setting,Profile,Avatar, WatchHistory,Favorite


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
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "profile_name", "profile_type", "customer", "avatar_preview", "action_buttons")
    list_filter = ("profile_type", "customer")
    search_fields = ("profile_name", "customer__name", "customer__email")
    ordering = ("id",)

    # Show avatar image preview
    def avatar_preview(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'image') and obj.avatar.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.avatar.image.url)
        return "-"
    avatar_preview.short_description = "Avatar"

    # Edit/Delete buttons
    def action_buttons(self, obj):
        return format_html(
            '<a class="button" style="background-color:#0d6efd;color:white;padding:2px 6px;border-radius:4px;" href="{}">Edit</a>&nbsp;'
            '<a class="button" style="background-color:#dc3545;color:white;padding:2px 6px;border-radius:4px;" href="{}">Delete</a>',
            f"/admin/customer/profile/{obj.id}/change/",
            f"/admin/customer/profile/{obj.id}/delete/",
        )
    action_buttons.short_description = "Actions"


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ("id", "image_preview", "is_active", "uploaded_at")
    list_filter = ("is_active", "uploaded_at")
    search_fields = ("image",)
    ordering = ("-uploaded_at",)
    actions = ["make_active", "make_inactive"]

    # Show actual image in the list
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected avatars as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected avatars as inactive"



@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "get_profile_name",
        "get_profile_code",
        "get_channel_name",
        "updated_at",
    )
    list_filter = (
        "updated_at",
        "channel__name",
        "profile__profile_type",
        "channel__category",
        "channel__language",
    )
    search_fields = (
        "customer__username",
        "profile__profile_name",
        "profile__profile_code",
        "channel__name",
        "channel__channel_id",
    )
    ordering = ("-updated_at",)
    readonly_fields = ("updated_at",)

    # Optional Jazzmin icons and colors
    class Media:
        css = {
            'all': ('admin/css/custom.css',)  # if you want custom styling
        }

    def get_profile_name(self, obj):
        return obj.profile.profile_name if obj.profile else "-"
    get_profile_name.short_description = "Profile Name"

    def get_profile_code(self, obj):
        return obj.profile.profile_code if obj.profile else "-"
    get_profile_code.short_description = "Profile Code"

    def get_channel_name(self, obj):
        return obj.channel.name if obj.channel else "-"
    get_channel_name.short_description = "Channel Name"



@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "get_profile_name",
        "get_profile_code",
        "get_channel_name",
        "updated_at",
    )
    list_filter = (
        "updated_at",
        "channel__name",
        "profile__profile_type",
        "channel__category",
        "channel__language",
    )
    search_fields = (
        "customer__username",
        "profile__profile_name",
        "profile__profile_code",
        "channel__name",
        "channel__channel_id",
    )
    ordering = ("-updated_at",)
    readonly_fields = ("updated_at",)

    def get_profile_name(self, obj):
        return obj.profile.profile_name if obj.profile else "-"
    get_profile_name.short_description = "Profile Name"

    def get_profile_code(self, obj):
        return obj.profile.profile_code if obj.profile else "-"
    get_profile_code.short_description = "Profile Code"

    def get_channel_name(self, obj):
        return obj.channel.name if obj.channel else "-"
    get_channel_name.short_description = "Channel Name"
    