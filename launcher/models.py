from django.db import models
from iptvengine.models import Channel 

class LauncherWallpaper(models.Model):
    name = models.CharField(max_length=200, default="Untitled")
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_video = models.BooleanField(default=False)
    media = models.FileField(
        upload_to="launcher/%Y/%m/%d/",
        default="launcher/default.jpg",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-updated_at"]

    def __str__(self):
        return f"{self.name} ({'Video' if self.is_video else 'Image'})"
    

class QuickNavigation(models.Model):
    TYPE_CHOICES = [
        ("LIVETV", "Live TV"),
        ("VOD", "Video on Demand"),
        ("FM", "FM Radio"),
        ("SETTINGS", "Settings"),
        ("PROFILE", "Profile"),
        ("APPS", "Apps"),
    ]

    title = models.CharField(max_length=200, default="Untitled Navigation")
    description = models.TextField(blank=True, null=True, default="No description available")

    # Backdrop image with default
    backdrop = models.ImageField(
        upload_to="quicknav/backdrops/",
        blank=True,
        null=True,
        default="quicknav/backdrops/default_backdrop.jpg"  # make sure this file exists in your media folder
    )

    # Video URL with default
    suggestedContentUrl = models.URLField(
        blank=True,
        null=True,
        default="http://example.com/default_video.m3u8"
    )

    isTrailer = models.BooleanField(default=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="LIVETV")

    def __str__(self):
        return f"{self.title} ({self.type})"


class SearchSuggestion(models.Model):
    suggestions = models.JSONField(default=list)  # ["Movies", "Sports", "News"]

    def __str__(self):
        return "Search Suggestions"

from django.core.exceptions import ValidationError
class Category(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ("QUICK_NAV", "Quick Navigation"),
        ("SEARCH", "Search Suggestions"),
        ("LIVE_TV", "Popular Live TV Channels"),
        ("FAVORITE", "Continue favorites"),
        ("WATCHLIST", "Continue Watching"),
    ]

    name = models.CharField(max_length=200, unique=True, default="New Category")
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES, default="QUICK_NAV")

    # Optional mappings
    search_suggestion = models.ForeignKey(
        "SearchSuggestion", blank=True, null=True, on_delete=models.SET_NULL
    )
    quick_navigation = models.ManyToManyField("QuickNavigation", blank=True)
    channel_genres = models.ManyToManyField("ChannelGenre", blank=True)
    

    def __str__(self):
        return self.name

def clean(self):
    from django.core.exceptions import ValidationError

    # Skip M2M validation if object is not saved yet
    if not self.pk:
        return

    if self.category_type == "QUICK_NAV" and not self.quick_navigation.exists():
        raise ValidationError("Please select at least one Quick Navigation item.")

    elif self.category_type == "SEARCH" and not self.search_suggestion:
        raise ValidationError("Please select a Search Suggestion item.")

    elif self.category_type == "LIVE_TV" and not self.channel_genres.exists():
        raise ValidationError("Please select at least one Channel Genre.")


class ChannelGenre(models.Model):
    # Choices for type
    BIG_LIVE_TV = 'BigLiveTv'
    LIVE_TV = 'LiveTv'
    CHANNEL_TYPE_CHOICES = [
        (BIG_LIVE_TV, 'Big Live TV'),
        (LIVE_TV, 'Live TV'),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True, default="")
    order = models.PositiveIntegerField(default=0)  # optional, for sorting
    channels = models.ManyToManyField(
        Channel,
        related_name="genres",  # allows channel.genres.all()
        blank=True               # optional, allows empty
    )
    type = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPE_CHOICES,
        default=LIVE_TV
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Channel Genre"
        verbose_name_plural = "Channel Genres"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.type})"
