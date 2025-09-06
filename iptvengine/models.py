from django.db import models
from django.utils import timezone

# DRM choices
DRM_CHOICES = [
    ("NONE", "None"),
    ("WIDEVINE", "Widevine"),
    ("FAIRPLAY", "FairPlay"),
    ("PLAYREADY", "PlayReady"),
]

# ------------------------------
# Language & Category
# ------------------------------
class Language(models.Model):
    name = models.CharField(max_length=100, unique=True, default="", db_index=True)
    image_url = models.URLField(max_length=255, blank=True, null=True, default="")
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, default="", db_index=True)
   
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return self.name


# ------------------------------
# Channel & Source/License
# ------------------------------
class Channel(models.Model):
    channel_id = models.CharField(max_length=50, unique=True, default="", db_index=True)
    name = models.CharField(max_length=200, default="", db_index=True)
    description = models.TextField(blank=True, null=True, default="")
    is_payed = models.BooleanField(default=False, db_index=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, db_index=True)
    logo = models.ImageField(upload_to="channels/logos/", blank=True, null=True, default="")
    order = models.PositiveIntegerField(default=0, db_index=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="channels", db_index=True,
        null=True, blank=True
    )
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="channels", db_index=True,
        null=True, blank=True
    )
    
    favorite = models.BooleanField(default=False, db_index=True)
    timeshift = models.PositiveIntegerField(default=0)  # hours
    adult = models.BooleanField(default=False, db_index=True)
    show_price = models.BooleanField(default=False)
    ppv = models.BooleanField(default=False)
    ppv_link = models.URLField(max_length=255, blank=True, null=True, default="")
    drm_type = models.CharField(max_length=50, choices=DRM_CHOICES, default="NONE", db_index=True)
      # Flatten relationships
    source_url = models.URLField(max_length=500, blank=True, null=True, default="", db_index=True)
    license_url = models.URLField(max_length=500, blank=True, null=True, default="", db_index=True)
    status = models.CharField(max_length=20, default="ACTIVE", db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return f"{self.name} ({'Paid' if self.is_payed else 'Free'})"

    def link(self):
        return self.logo
    link.short_description = "Channel Link"

class SourceHeader(models.Model):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="source_headers",
        null=True,      # allows NULL in DB
        blank=True,     # allows blank in forms/admin
        default=None    # no forced default
    )
    key = models.CharField(max_length=255, default="User-Agent")
    value = models.CharField(max_length=500, default="Mozilla/5.0")

    def __str__(self):
        return f"{self.key}: {self.value}"


class LicenseHeaderItem(models.Model):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="license_headers",
        null=True,      # allows NULL in DB
        blank=True,     # allows blank in forms/admin
        default=None    # no forced default
    )
    key = models.CharField(max_length=255, default="Authorization")
    value = models.CharField(max_length=500, default="Bearer token_here")

    def __str__(self):
        return f"{self.key}: {self.value}"


# ------------------------------
# Groups, Tariffs, Radio, Device
# ------------------------------
class ChannelGroup(models.Model):
    name = models.CharField(max_length=200, default="", db_index=True)
    channels = models.ManyToManyField(Channel, related_name="groups", blank=True)
  
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.name


class Tariff(models.Model):
    name = models.CharField(max_length=200, unique=True, default="", db_index=True)
    channel_groups = models.ManyToManyField(ChannelGroup, related_name="tariffs", blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.name





class Radio(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="radios",  null=True,    blank=True )
    name = models.CharField(max_length=100, default="Unknown Radio")  # default name
    source = models.URLField(max_length=500, default="http://example.com/stream") 
    logo = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_fm = models.BooleanField(default=True)  # default FM

    def __str__(self):
        return f"{self.name} ({self.language.name})"

    def save(self, *args, **kwargs):
        if self.is_fm is None:   # in case someone explicitly passes None
            self.is_fm = True
        super().save(*args, **kwargs)