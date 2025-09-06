from django.conf import settings
from ui.models import UITweaks
from ui.jazzmin_dynamic import get_dynamic_jazzmin_settings

def apply_jazzmin_tweaks():
    tweaks = UITweaks.objects.filter(is_active=True).first()
    if tweaks:
        return {
            "navbar_small_text": tweaks.navbar_small_text,
            "footer_small_text": tweaks.footer_small_text,
            "body_small_text": tweaks.body_small_text,
            "brand_small_text": tweaks.brand_small_text,
            "brand_colour": tweaks.brand_colour,
            "accent": tweaks.accent,
            "navbar": tweaks.navbar,
            "no_navbar_border": tweaks.no_navbar_border,
            "navbar_fixed": tweaks.navbar_fixed,
            "layout_boxed": tweaks.layout_boxed,
            "footer_fixed": tweaks.footer_fixed,
            "sidebar_fixed": tweaks.sidebar_fixed,
            "sidebar": tweaks.sidebar,
            "sidebar_nav_small_text": tweaks.sidebar_nav_small_text,
            "sidebar_disable_expand": tweaks.sidebar_disable_expand,
            "sidebar_nav_child_indent": tweaks.sidebar_nav_child_indent,
            "sidebar_nav_compact_style": tweaks.sidebar_nav_compact_style,
            "sidebar_nav_legacy_style": tweaks.sidebar_nav_legacy_style,
            "sidebar_nav_flat_style": tweaks.sidebar_nav_flat_style,
            "theme": tweaks.theme,
            "dark_mode_theme": tweaks.dark_mode_theme,
            "button_classes": {
                "primary": tweaks.primary_button,
                "secondary": tweaks.secondary_button,
                "info": tweaks.info_button,
                "warning": tweaks.warning_button,
                "danger": tweaks.danger_button,
                "success": tweaks.success_button,
            },
        }
    return {}

class JazzminReloadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Apply tweaks dynamically before view is called
        settings.JAZZMIN_UI_TWEAKS = apply_jazzmin_tweaks()
        settings.JAZZMIN_SETTINGS = get_dynamic_jazzmin_settings()
        return self.get_response(request)


def get_current_ui_config():
    return UITweaks.objects.filter(is_active=True).first() or UITweaks()