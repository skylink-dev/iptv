from django.db import models

class MovieCategory(models.Model):
    category_id = models.CharField(max_length=50, unique=True, blank=True, null=True)  # API category id
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or "Unnamed Category"


class Movie(models.Model):
    category = models.ForeignKey(MovieCategory, on_delete=models.CASCADE, related_name="movies", null=True, blank=True)
    movie_id = models.CharField(max_length=50, blank=True, null=True)  # API movie id
    name = models.CharField(max_length=255, blank=True, null=True, default="Untitled Movie")
    poster = models.URLField(blank=True, null=True, default="")
    backdrop = models.URLField(blank=True, null=True, default="")
    languages = models.JSONField(default=list, blank=True)  # default empty list
    quality = models.CharField(max_length=50, blank=True, null=True, default="HD")
    rating = models.CharField(max_length=10, blank=True, null=True, default="0")
    isPremiumFirst = models.BooleanField(default=False)
    isPremium = models.BooleanField(default=False)
    watchingCount = models.CharField(max_length=10, blank=True, null=True, default="0")
    isAdult = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True, default="")
    trailer = models.URLField(blank=True, null=True, default="")
    isTrailer = models.BooleanField(default=False)
    release_year = models.PositiveIntegerField(blank=True, null=True)
    source = models.URLField(blank=True, null=True, default="")    
    # New field: indicates if the movie needs to navigate to another app
    is_intent = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.name or 'Untitled Movie'} ({self.category.name if self.category else 'No Category'})"



class MovieSlider(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="slider_items",
        null=True,       # can be empty in DB
        blank=True       # can be empty in forms/admin
    )
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Slider: {self.movie.name if self.movie else 'No Movie'}"