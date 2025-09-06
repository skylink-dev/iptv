from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class UiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ui'

    def ready(self):
        try:
            from ui.models import UITweaks
            tweaks = UITweaks.objects.filter(is_active=True).first()

            if tweaks:
                logger.info("✅ Jazzmin loaded from DB")
                settings.JAZZMIN_UI_TWEAKS = {
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
            else:
                logger.warning("⚠️ No active Jazzmin UI tweaks found.")
                settings.JAZZMIN_UI_TWEAKS = {}
        except Exception as e:
            logger.error("❌ Jazzmin tweak load error in apps.py: %s", str(e))
            settings.JAZZMIN_UI_TWEAKS = {}
