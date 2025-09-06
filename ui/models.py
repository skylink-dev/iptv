from django.db import models

# Theme choices for Jazzmin
THEME_CHOICES = [
    ("cosmo", "Cosmo"),
    ("flatly", "Flatly"),
    ("cyborg", "Cyborg"),
    ("slate", "Slate"),
    ("superhero", "Superhero"),
    ("lux", "Lux"),
    ("litera", "Litera"),
    ("simplex", "Simplex"),
    ("solar", "Solar"),
    ("darkly", "Darkly"),
]

COLOR_CHOICES = [
    ("navbar-white", "White"),
    ("navbar-dark", "Dark"),
    ("navbar-light", "Light"),
    ("navbar-primary", "Primary"),
    ("navbar-success", "Success"),
    ("navbar-info", "Info"),
    ("navbar-warning", "Warning"),
    ("navbar-danger", "Danger"),
]

SIDEBAR_CHOICES = [
    ("sidebar-dark-primary", "Dark Primary"),
    ("sidebar-dark-info", "Dark Info"),
    ("sidebar-light", "Light"),
]

BUTTON_STYLE_CHOICES = [
    ("btn-primary", "Primary"),
    ("btn-secondary", "Secondary"),
    ("btn-info", "Info"),
    ("btn-warning", "Warning"),
    ("btn-danger", "Danger"),
    ("btn-success", "Success"),
]



class UITweaks(models.Model):



    name = models.CharField(max_length=100, default="theme1")
    is_active = models.BooleanField(default=False)
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default="cosmo")
    navbar = models.CharField(max_length=50, choices=COLOR_CHOICES, default="navbar-dark")
    brand_colour = models.CharField(max_length=50, choices=COLOR_CHOICES, default="navbar-success")
    sidebar = models.CharField(max_length=50, choices=SIDEBAR_CHOICES, default="sidebar-dark-info")
    accent = models.CharField(max_length=50, default="accent-teal")

    # Toggle Options
    navbar_small_text = models.BooleanField(default=False)
    footer_small_text = models.BooleanField(default=False)
    body_small_text = models.BooleanField(default=False)
    brand_small_text = models.BooleanField(default=False)
    no_navbar_border = models.BooleanField(default=False)
    navbar_fixed = models.BooleanField(default=True)
    layout_boxed = models.BooleanField(default=False)
    footer_fixed = models.BooleanField(default=False)
    sidebar_fixed = models.BooleanField(default=True)
    sidebar_nav_small_text = models.BooleanField(default=False)
    sidebar_disable_expand = models.BooleanField(default=False)
    sidebar_nav_child_indent = models.BooleanField(default=False)
    sidebar_nav_compact_style = models.BooleanField(default=False)
    sidebar_nav_legacy_style = models.BooleanField(default=False)
    sidebar_nav_flat_style = models.BooleanField(default=False)

    # Optional dark mode field
    dark_mode_theme = models.CharField(max_length=50, null=True, blank=True, default="darkly")
    #Button 
    primary_button = models.CharField(max_length=20, choices=BUTTON_STYLE_CHOICES, default="btn-primary", verbose_name="Primary Button")
    secondary_button = models.CharField(max_length=20, choices=BUTTON_STYLE_CHOICES, default="btn-secondary", verbose_name="Secondary Button")
    info_button = models.CharField(max_length=20, choices=BUTTON_STYLE_CHOICES, default="btn-info", verbose_name="Info Button")
    warning_button = models.CharField(max_length=20, choices=BUTTON_STYLE_CHOICES, default="btn-warning", verbose_name="Warning Button")
    danger_button = models.CharField(max_length=20, choices=BUTTON_STYLE_CHOICES, default="btn-danger", verbose_name="Danger Button")
    success_button = models.CharField(max_length=20, choices=BUTTON_STYLE_CHOICES, default="btn-success", verbose_name="Success Button")


    def __str__(self):
        return "Jazzmin UI Tweaks"

    class Meta:
        verbose_name = "Appearance Setting"
        verbose_name_plural = "Appearance Settings"




   

    
class JazzminSettings(models.Model):
    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
    site_title = models.CharField(max_length=100, default="IPTV Engine")
    site_header = models.CharField(max_length=100, default="IPTV")
    site_brand = models.CharField(max_length=100, default="IPTV Engine")
    site_icon = models.CharField(max_length=255, default="images/favicon.png")
    site_logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    welcome_sign = models.CharField(max_length=255, default="Welcome to the Skylink IPTV")
    copyright = models.CharField(max_length=100, default="Skylink IPTV")
    user_avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # New fields
    show_sidebar = models.BooleanField(default=True)
    navigation_expanded = models.BooleanField(default=False)
    default_icon_parents = models.CharField(max_length=100, default="fas fa-chevron-circle-right")
    default_icon_children = models.CharField(max_length=100, default="fas fa-arrow-circle-right")
    related_modal_active = models.BooleanField(default=False)

    def __str__(self):
        return self.site_title

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "Jazzmin Settings"
    
    def save(self, *args, **kwargs):
        if self.is_active:
            JazzminSettings.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)