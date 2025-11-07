from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import MovieCategory, Movie, MovieSlider
from .utils import fetch_and_save_movies  # utility function to fetch API movies

@admin.register(MovieCategory)
class MovieCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)

    # Use a custom template for change_list to add button
    change_list_template = "admin/movies/moviecategory_changelist.html"

    # Add custom URL for fetch button
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-movies/', self.admin_site.admin_view(self.fetch_movies), name="fetch_movies"),
        ]
        return custom_urls + urls

    # The function to fetch movies from API
    def fetch_movies(self, request):
        try:
            count = fetch_and_save_movies()  # call utility function
            self.message_user(request, f"Fetched and saved movies for {count} categories.", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error fetching movies: {e}", level=messages.ERROR)
        return redirect("..")

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "rating", "isPremium")
    list_display_links = ("name",)
    list_filter = ("category", "isPremium", "quality", "isAdult")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(MovieSlider)
class MovieSliderAdmin(admin.ModelAdmin):
    list_display = ("movie", "order", "is_active")   # columns to show
    list_editable = ("order", "is_active")           # editable from list view
    search_fields = ("movie__name",)                 # search movies by name
    list_filter = ("is_active",)  