from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
import nested_admin
from .models import (
    Tariff, Channel, ChannelGroup,
    Language, Category, 
     Radio, SourceHeader, LicenseHeaderItem
)
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from import_export.admin import ExportMixin
# iptvengine/admin.py
import requests
from decimal import Decimal, InvalidOperation
from django.contrib import admin, messages
from django.shortcuts import redirect,render
from django.urls import path
from django.http import HttpResponse
import csv
from django.core.files.base import ContentFile
from django.conf import settings
import os
# ------------------------------
# Reusable Actions
# ------------------------------
class CustomAdminActions(admin.ModelAdmin):
    def custom_actions(self, obj):
        edit_url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk])
        delete_url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete", args=[obj.pk])
        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Edit</a> '
            '<a class="btn btn-sm btn-danger" href="{}">Delete</a>',
            edit_url, delete_url
        )
    custom_actions.short_description = "Actions"

class SourceHeaderInline(admin.TabularInline):
    model = SourceHeader
    extra = 1


class LicenseHeaderItemInline(admin.TabularInline):
    model = LicenseHeaderItem
    extra = 1


# ------------------------------
# Admins
# ------------------------------
@admin.register(Tariff)
class TariffAdmin(CustomAdminActions):
    list_display = ("id", "name", "display_channel_groups", "custom_actions")
    search_fields = ("name",)
    list_filter = ("channel_groups",)

    def display_channel_groups(self, obj):
        return ", ".join([group.name for group in obj.channel_groups.all()])
    display_channel_groups.short_description = "Channel Groups"
# Resource for Import/Export
class ChannelResource(resources.ModelResource):
    class Meta:
        model = Channel
        fields = (
            "id",
            "channel_id",
            "name",
            "category__name",
            "language__name",
            "price",
            "is_payed",
            "order",
            "favorite",
            "timeshift",
            "adult",
            "show_price",
            "ppv",
            "ppv_link",
            "source_url",
            "status",
        )
        export_order = fields

# ----------------------------
# Channel Admin
# ----------------------------
@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "channel_id", "price", "is_payed", "order", "status", "logo_tag", "action_buttons")
    search_fields = ("name", "channel_id")
    list_filter = ("is_payed", "status", "created_at")
    actions = []
    change_list_template = "admin/iptvengine/channel/change_list.html"
    readonly_fields = ("logo_tag",) 
    
    def logo_tag(self, obj):
        if obj.logo:
            # If obj.logo.url does not work, build the URL manually
            logo_url = obj.logo.url if hasattr(obj.logo, 'url') else f"{settings.MEDIA_URL}{obj.logo}"
            return format_html('<img src="{}" style="height:40px;"/>', logo_url)
        return "-"
    logo_tag.short_description = "Logo"

    def action_buttons(self, obj):
        """Custom Edit/Delete buttons in list view"""
        edit_url = reverse("admin:iptvengine_channel_change", args=[obj.pk])
        delete_url = reverse("admin:iptvengine_channel_delete", args=[obj.pk])

        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Edit</a> '
            '<a class="btn btn-sm btn-danger" href="{}">Delete</a>',
            edit_url, delete_url
        )

    action_buttons.short_description = "Actions"
    action_buttons.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "fetch-channels/",
                self.admin_site.admin_view(self.fetch_channels_view),
                name="fetch-channels",
            ),
            path(
                "export-channels/",
                self.admin_site.admin_view(self.export_channels_view),
                name="export-channels",
            ),
            path(
                "import-channels/",
                self.admin_site.admin_view(self.import_channels_view),
                name="import-channels",
            ),
        ]
        return custom_urls + urls

    # ---------------- Fetch Channels ----------------
    def fetch_channels_view(self, request):
        self._fetch_channels(request)
        self.message_user(request, "✅ Channels fetched successfully!", level=messages.SUCCESS)
        return redirect("..")

    def _fetch_channels(self, request):
        import requests

        url = "http://172.19.0.1/digitaltv/getTvChannelsNew"
        payload = {"uuid": "5b0c8177-c484-4b85-960d-48d3238abb05"}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.message_user(request, f"API call failed: {e}", level=messages.ERROR)
            return

        categories = data.get("categories", [])
        created_count, updated_count = 0, 0

        for category_data in categories:
            cat_obj, _ = Category.objects.get_or_create(
                name=category_data.get("name", "Uncategorized")
            )

            for ch in category_data.get("channels", []):
                # Safe language extraction
                languages = ch.get("languages")
                if languages and len(languages) > 0:
                    ch_lang_name = languages[0].get("name", "Unknown")
                else:
                    ch_lang_name = "Unknown"
                
                ch_lang_obj, _ = Language.objects.get_or_create(name=ch_lang_name)

                # Convert price safely
                price_val = ch.get("price", "0.00")
                try:
                    price_val = Decimal(price_val)
                except (InvalidOperation, TypeError):
                    price_val = Decimal("0.00")

                obj, created = Channel.objects.update_or_create(
                    channel_id=str(ch["id"]),
                    defaults={
                        "name": ch.get("name", ""),
                        "is_payed": ch.get("isPayed", False),
                        "price": price_val,
                        "order": ch.get("order", 0),
                        "category": cat_obj,
                        "language": ch_lang_obj,
                        "favorite": ch.get("favorite", False),
                        "timeshift": ch.get("timeshift", 0),
                        "adult": ch.get("adult", False),
                        "show_price": ch.get("showPrice", False),
                        "ppv": ch.get("ppv", False),
                        "ppv_link": ch.get("ppvLink", "") or "",
                        "source_url": ch.get("source", ""),
                        "status": "ACTIVE",
                        #"logo": None,
                    },
                )

                                
               
                # --- Handle logo download ---
                # --- Handle logo download ---
                logo_url = ch.get("logo")

                # validate logo_url (must be non-empty string starting with http)
                if not logo_url or not isinstance(logo_url, str) or not logo_url.startswith(("http://", "https://")):
                    # fallback if missing or invalid
                    logo_url = f"http://172.19.0.1/static/tv/logos/{ch['id']}.png"

                if logo_url:
                    try:
                        if not obj.logo:  # check if logo field is empty in DB
                            r = requests.get(logo_url, timeout=10)
                            if r.status_code == 200:
                                # create filename: channelid_name.png
                                safe_name = obj.name.lower().replace(" ", "_")
                                filename = f"{obj.channel_id}_{safe_name}.png"

                                # full path in MEDIA_ROOT
                                file_path = os.path.join(settings.MEDIA_ROOT, "channels/logos", filename)

                                # check if file already exists
                                if not os.path.exists(file_path):
                                    obj.logo.save(filename, ContentFile(r.content), save=True)
                                else:
                                    print(f"✅ Logo already exists for {obj.name}, skipping download.")
                        else:
                            print(f"✅ Logo already set in DB for {obj.name}, skipping download.")

                    except Exception as e:
                        print(f"⚠️ Failed to download logo for {obj.name}: {e}")

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.message_user(
            request,
            f"✅ Channels import finished: {created_count} created, {updated_count} updated.",
            level=messages.SUCCESS,
        )

    # ---------------- Export Channels ----------------
    def export_channels_view(self, request):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="channels.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "ID","Channel ID","Name","Description","Is Paid","Price","Logo","Order",
            "Category","Language","Favorite","Timeshift","Adult","Show Price","PPV",
            "PPV Link","DRM Type","Source URL","License URL","Status","Created At"
        ])

        for ch in Channel.objects.all():
            writer.writerow([
                ch.id,
                ch.channel_id,
                ch.name,
                ch.description,
                ch.is_payed,
                ch.price,
                ch.logo.url if ch.logo else "",
                ch.order,
                ch.category.name if ch.category else "",
                ch.language.name if ch.language else "",
                ch.favorite,
                ch.timeshift,
                ch.adult,
                ch.show_price,
                ch.ppv,
                ch.ppv_link or "",
                ch.drm_type,
                ch.source_url or "",
                ch.license_url or "",
                ch.status,
                ch.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        return response

    # ---------------- Import Channels ----------------
    def import_channels_view(self, request):
        if request.method == "POST" and request.FILES.get("csv_file"):
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)

            created_count, updated_count = 0, 0

            for row in reader:
                cat_name = row.get("Category", "").strip()
                category_obj = None
                if cat_name:
                    category_obj, _ = Category.objects.get_or_create(name=cat_name)

                lang_name = row.get("Language", "").strip()
                language_obj = None
                if lang_name:
                    language_obj, _ = Language.objects.get_or_create(name=lang_name)

                try:
                    price_val = float(row.get("Price", 0))
                except ValueError:
                    price_val = 0.0

                obj, created = Channel.objects.update_or_create(
                    channel_id=row.get("Channel ID", ""),
                    defaults={
                        "name": row.get("Name", ""),
                        "description": row.get("Description", ""),
                        "is_payed": row.get("Is Paid", "").lower() in ["true","1","yes"],
                        "price": price_val,
                        "logo": row.get("Logo", ""),
                        "order": int(row.get("Order", 0)),
                        "category": category_obj,
                        "language": language_obj,
                        "favorite": row.get("Favorite", "").lower() in ["true","1","yes"],
                        "timeshift": int(row.get("Timeshift", 0)),
                        "adult": row.get("Adult", "").lower() in ["true","1","yes"],
                        "show_price": row.get("Show Price", "").lower() in ["true","1","yes"],
                        "ppv": row.get("PPV", "").lower() in ["true","1","yes"],
                        "ppv_link": row.get("PPV Link", ""),
                        "drm_type": row.get("DRM Type", "NONE"),
                        "source_url": row.get("Source URL", ""),
                        "license_url": row.get("License URL", ""),
                        "status": row.get("Status", "ACTIVE"),
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            messages.success(
                request,
                f"✅ Channels imported: {created_count} created, {updated_count} updated."
            )
            return redirect("..")

        return render(request, "admin/iptvengine/channel/import_csv.html")

@admin.register(ChannelGroup)
class ChannelGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "display_channels", "order", "created_at", "updated_at", "action_buttons")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")

    def display_channels(self, obj):
        channels = obj.channels.all()
        if len(channels) > 5:
            first_five = ", ".join(c.name for c in channels[:5])
            return f"{first_five} +{len(channels)-5} more"
        return ", ".join(c.name for c in channels)
    display_channels.short_description = "Channels"

    def action_buttons(self, obj):
        """Custom Edit/Delete buttons in list view"""
        edit_url = reverse("admin:iptvengine_channelgroup_change", args=[obj.pk])
        delete_url = reverse("admin:iptvengine_channelgroup_delete", args=[obj.pk])

        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Edit</a> '
            '<a class="btn btn-sm btn-danger" href="{}">Delete</a>',
            edit_url, delete_url
        )

    action_buttons.short_description = "Actions"
    action_buttons.allow_tags = True






class LanguageResource(resources.ModelResource):
    class Meta:
        model = Language
        fields = ("id", "name",)  # fields to export/import
        export_order = ("id", "name")
   

# Register in admin with import/export support
from django.utils.html import format_html

@admin.register(Language)
class LanguageAdmin(ImportExportModelAdmin):
    resource_class = LanguageResource
    list_display = ("id", "name", "image_tag", "tv_banner_tag", "action_buttons")
    search_fields = ("name",)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"
    image_tag.short_description = "Image"

    def tv_banner_tag(self, obj):
        if obj.tv_banner:
            return format_html('<img src="{}" width="100" />', obj.tv_banner.url)
        return "-"
    tv_banner_tag.short_description = "TV Banner"

    def action_buttons(self, obj):
        edit_url = reverse("admin:iptvengine_language_change", args=[obj.pk])
        delete_url = reverse("admin:iptvengine_language_delete", args=[obj.pk])
        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Edit</a> '
            '<a class="btn btn-sm btn-danger" href="{}">Delete</a>',
            edit_url, delete_url
        )
    action_buttons.short_description = "Actions"
    action_buttons.allow_tags = True


@admin.register(Category)
class CategoryAdmin(CustomAdminActions):
    list_display = ("id", "name", "custom_actions")
    search_fields = ("name",)
    def action_buttons(self, obj):
        """Custom Edit/Delete buttons in list view"""
        edit_url = reverse("admin:iptvengine_category_change", args=[obj.pk])
        delete_url = reverse("admin:iptvengine_category_delete", args=[obj.pk])

        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Edit</a> '
            '<a class="btn btn-sm btn-danger" href="{}">Delete</a>',
            edit_url, delete_url
        )

    action_buttons.short_description = "Actions"
    action_buttons.allow_tags = True
    


@admin.register(Radio)
class RadioAdmin(admin.ModelAdmin):
    list_display = ("name", "language", "order", "is_fm", "logo", "action_buttons")  # columns to show
    list_filter = ("language", "is_fm", "logo")  # add filter sidebar
    search_fields = ("name", "language__name")  # search by radio name or language
    ordering = ("language", "order")  # default ordering
    def action_buttons(self, obj):
        """Custom Edit/Delete buttons in list view"""
        edit_url = reverse("admin:iptvengine_radio_change", args=[obj.pk])
        delete_url = reverse("admin:iptvengine_radio_delete", args=[obj.pk])

        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Edit</a> '
            '<a class="btn btn-sm btn-danger" href="{}">Delete</a>',
            edit_url, delete_url
        )

    action_buttons.short_description = "Actions"
    action_buttons.allow_tags = True
