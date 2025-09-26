from .models import JazzminSettings

def get_dynamic_jazzmin_settings():
    settings_obj = JazzminSettings.objects.filter(is_active=True).first()
    if not settings_obj:
        return {}

    return {
        "site_title": settings_obj.site_title,
        "site_header": settings_obj.site_header,
        "site_brand": settings_obj.site_brand,
        "site_icon": settings_obj.site_icon,
        "site_logo": "media/logos/skylink_logo_pDCDUm8.png",
        "site_logo_classes": "img-circle elevation-3",
        "welcome_sign": settings_obj.welcome_sign,
        "copyright": settings_obj.copyright,
        "user_avatar": settings_obj.user_avatar.url if settings_obj.user_avatar else None,

        "show_sidebar": settings_obj.show_sidebar,
        "navigation_expanded": settings_obj.navigation_expanded,
        "order_with_respect_to": ["auth", "users", "iptvengine"],

        "icons": {
           "iptvengine": "fas fa-tv", "ui": "fas fa-paint-brush", "customer": "fas fa-user-circle", "partner": "fas fa-handshake", "auth": "fas fa-users-cog", "auth.user": "fas fa-user",
        },

        "topmenu_links": [
            {"name": "Dashboard", "url": "admin:index"},  # Default Django dashboard
            {"name": "Customer", "url": "/admin/customer/", "permissions": ["customer.view_customer"]},
            {"name": "IPTV Engine", "url": "/admin/iptvengine/", "permissions": ["iptvengine.view_channel"]},
            {"name": "Users", "model": "auth.User"},  # Using model reference
        ],


        "side_menu": [
            {
                "app": "iptvengine",
                "label": "▶ IPTV Engine",
                "icon": "fas fa-satellite-dish",
                "models": [
                    {"model": "iptvengine.language", "name": "🌐 Languages"},
                    {"model": "iptvengine.category", "name": "🏷 Categories"},
                    {"model": "iptvengine.tariff", "name": "💰 Tariffs"},
                    {"model": "iptvengine.device", "name": "🛰 Devices"},
                    {"model": "iptvengine.radio", "name": "📻 Radio"},
                ],
            }, {
                "app": "customer",
                "label": "▶ Customer",
                "icon": "fas fa-user-circle",
                "models": [
                    {"model": "customer.customer", "name": "👤 Customers"},
                    {"model": "customer.profile", "name": "📝 Profiles"},
                    {"model": "customer.Favorite", "name": "⭐ Favorites"},
                ],
            },
        ],

        "model_icons": {
            "iptvengine.language": "fas fa-language",
            "iptvengine.category": "fas fa-tags",
            "iptvengine.channel": "fas fa-tv",
            "iptvengine.channelsourceheader": "fas fa-code",
            "iptvengine.licenseheader": "fas fa-file-contract",
            "iptvengine.channelgroup": "fas fa-layer-group",
            "iptvengine.tariff": "fas fa-money-bill",
            "iptvengine.device": "fas fa-tablet-alt",
            "iptvengine.radio": "fas fa-broadcast-tower",
            "customer.Favorite": "fas fa-star",
        },

        "related_modal_active": settings_obj.related_modal_active,
        "show_ui_builder": True,
        "changeform_format": "tabs",
    }
