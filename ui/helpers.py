from django.conf import settings

def get_jazzmin_button_class(type_name, default="btn btn-sm"):
    tweaks = getattr(settings, "JAZZMIN_UI_TWEAKS", {})
    button_classes = tweaks.get("button_classes", {})
    return f"{default} {button_classes.get(type_name, '')}"
