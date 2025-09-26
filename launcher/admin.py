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
    list_display = ("title", "type", "backdrop", "isTrailer", "edit_button", "delete_button")
    list_filter = ("type", "isTrailer")
    search_fields = ("title", "description")
    readonly_fields = ("id",)

    def edit_button(self, obj):
        return get_edit_button(obj, "launcher", "quicknavigation")

    def delete_button(self, obj):
        return get_delete_button(obj, "launcher", "quicknavigation")


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
