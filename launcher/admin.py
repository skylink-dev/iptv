from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import LauncherWallpaper, Category, QuickNavigation, SearchSuggestion, ChannelGenre


# --- Utility functions for buttons ---
def get_edit_button(obj, app_label, model_name):
    url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk])
    return format_html('<a class="btn btn-info btn-sm" href="{}">Edit</a>', url)
get_edit_button.short_description = "Edit"


def get_delete_button(obj, app_label, model_name):
    url = reverse(f"admin:{app_label}_{model_name}_delete", args=[obj.pk])
    return format_html('<a class="btn btn-danger btn-sm" href="{}">Delete</a>', url)
get_delete_button.short_description = "Delete"


# --- LauncherWallpaper Admin ---
@admin.register(LauncherWallpaper)
class LauncherWallpaperAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "order",
        "is_video",
        "is_active",
        "updated_at",
        "edit_button",
        "delete_button",
    )
    list_editable = ("order", "is_active")
    list_filter = ("is_video", "is_active")
    search_fields = ("name",)
    readonly_fields = ("id",)

    def edit_button(self, obj):
        return get_edit_button(obj, "launcher", "launcherwallpaper")

    def delete_button(self, obj):
        return get_delete_button(obj, "launcher", "launcherwallpaper")


# --- QuickNavigation Admin ---
@admin.register(QuickNavigation)
class QuickNavigationAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "preview_image", "preview_backdrop", "isTrailer", "edit_button", "delete_button")
    list_filter = ("type", "isTrailer")
    search_fields = ("title", "description")
    readonly_fields = ("id", "image_preview", "backdrop_preview")

    fieldsets = (
        (None, {
            "fields": ("title", "description", "type", "isTrailer")
        }),
        ("Media", {
            "fields": ("image", "image_preview", "backdrop", "backdrop_preview", "suggestedContentUrl")
        }),
    )

    def edit_button(self, obj):
        return get_edit_button(obj, "launcher", "quicknavigation")

    def delete_button(self, obj):
        return get_delete_button(obj, "launcher", "quicknavigation")

    # 👇 Show preview in admin list
    def preview_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="60" height="40" style="object-fit:cover; border-radius:4px;" />'
        return "No Image"
    preview_image.allow_tags = True
    preview_image.short_description = "Image"

    def preview_backdrop(self, obj):
        if obj.backdrop:
            return f'<img src="{obj.backdrop.url}" width="100" height="50" style="object-fit:cover; border-radius:4px;" />'
        return "No Backdrop"
    preview_backdrop.allow_tags = True
    preview_backdrop.short_description = "Backdrop"

    # 👇 For readonly preview inside form
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="200" height="120" style="object-fit:cover; border-radius:6px;" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = "Image Preview"

    def backdrop_preview(self, obj):
        if obj.backdrop:
            return f'<img src="{obj.backdrop.url}" width="300" height="150" style="object-fit:cover; border-radius:6px;" />'
        return "No Backdrop"
    backdrop_preview.allow_tags = True
    backdrop_preview.short_description = "Backdrop Preview"

# --- SearchSuggestion Admin ---
@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = ("id", "suggestions_list", "edit_button", "delete_button")
    
    def suggestions_list(self, obj):
        return ", ".join(obj.suggestions)
    suggestions_list.short_description = "Suggestions"

    def edit_button(self, obj):
        return get_edit_button(obj, "launcher", "searchsuggestion")

    def delete_button(self, obj):
        return get_delete_button(obj, "launcher", "searchsuggestion")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "edit_button", "delete_button")
    readonly_fields = ("id",)

    def edit_button(self, obj):
        return get_edit_button(obj, "launcher", "category")  # pass app_label & model_name
    edit_button.short_description = "Edit"

    def delete_button(self, obj):
        return get_delete_button(obj, "launcher", "category")  # pass app_label & model_name
    delete_button.short_description = "Delete"

from django.contrib import admin
from .models import ChannelGenre, Channel

@admin.register(ChannelGenre)
class ChannelGenreAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "description", "order"]
    filter_horizontal = ["channels"]
