from django.contrib import admin
from .models import UITweaks, JazzminSettings
from django.utils.html import format_html
from django.urls import reverse
from .middleware import get_current_ui_config


@admin.register(UITweaks)
class UITweaksAdmin(admin.ModelAdmin):
    list_display = ("name", "theme", "navbar", "sidebar", "accent", "is_active", "custom_actions")
    list_filter = ("is_active", "theme", "navbar", "sidebar")
    search_fields = ("name",)
    list_editable = ["is_active"]
    actions = ["reset_theme"]

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            UITweaks.objects.exclude(id=obj.id).update(is_active=False)
        super().save_model(request, obj, form, change)

    # admin.py

    def custom_actions(self, obj):
        active_config = get_current_ui_config()

        # Fallbacks to standard Bootstrap classes if not defined
        primary_btn = getattr(active_config, 'primary_button', 'btn-primary')
        danger_btn = getattr(active_config, 'danger_button', 'btn-danger')

        edit_class = f"btn btn-sm {primary_btn}"
        delete_class = f"btn btn-sm {danger_btn}"

        edit_url = reverse("admin:ui_uitweaks_change", args=[obj.pk])
        delete_url = reverse("admin:ui_uitweaks_delete", args=[obj.pk])

        return format_html(
            '<a class="{}" href="{}">Edit</a> '
            '<a class="{}" href="{}">Delete</a>',
            edit_class, edit_url, delete_class, delete_url
        )

    custom_actions.short_description = "Actions"

    @admin.action(description="Reset to default Jazzmin theme")
    def reset_theme(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(JazzminSettings)
class JazzminSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_title", "site_brand", "is_active"]