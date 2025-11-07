from rest_framework import serializers
from .models import LauncherWallpaper, Category, QuickNavigation, SearchSuggestion, ChannelGenre
from iptvengine.models import Channel
from customer.models import Favorite, WatchHistory
from iptvengine.serializers import ChannelSerializer
class LauncherWallpaperSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()

    class Meta:
        model = LauncherWallpaper
        fields = ["id", "name", "order", "is_video", "media", "is_active"]

    def get_media(self, obj):
        request = self.context.get("request")
        if obj.media:
            return request.build_absolute_uri(obj.media.url) if request else obj.media.url
        return None

class QuickNavigationSerializer(serializers.ModelSerializer):
    focused_image = serializers.SerializerMethodField()
    unfocused_image = serializers.SerializerMethodField()
    backdrop = serializers.SerializerMethodField()

    class Meta:
        model = QuickNavigation
        fields = [
            "id",
            "title",
            "description",
            "focused_image",
            "unfocused_image",
            "backdrop",
            "suggestedContentUrl",
            "isTrailer",
            "type",
            "order"
        ]

    def get_focused_image(self, obj):
        return self._build_full_url(obj.focusedImage)

    def get_unfocused_image(self, obj):
        return self._build_full_url(obj.unfocusedImage)

    def get_backdrop(self, obj):
        return self._build_full_url(obj.backdrop)

    def _build_full_url(self, file_field):
        if not file_field:
            return None
        request = self.context.get("request")
        try:
            if request:
                return request.build_absolute_uri(file_field.url)
            else:
                # fallback if no request in context
                domain = getattr(settings, "SITE_DOMAIN", "http://localhost:8000")
                return f"{domain}{file_field.url}"
        except ValueError:
            return None


class SearchSuggestionSerializer(serializers.ModelSerializer):
    suggestions = serializers.ListField(child=serializers.CharField(), default=list)

    class Meta:
        model = SearchSuggestion
        fields = ["id", "suggestions"]


# class ChannelSerializer(serializers.ModelSerializer):
#     source_headers = serializers.SerializerMethodField()
#     license_headers = serializers.SerializerMethodField()
#     class Meta:
#         model = Channel
#         fields = ["id", "name", "type", "description", "order", "channels", "is_payed", "price", "logo",    "order", "favorite", "timeshift", "adult", "show_price",  "ppv", "ppv_link", "drm_type", "status", "category", "language", "source_url", "license_url","logo",
#             "source_headers", "license_headers" ]
#     def get_source_headers(self, obj):
#         """
#         Convert source headers list -> dict
#         """
#         headers = obj.source_headers.all()
#         if not headers.exists():
#             return None
#         return {h.key: h.value for h in headers}
#     def get_license_headers(self, obj):
#         """
#         Convert license headers list -> dict, return null if empty
#         """
#         headers = obj.license_headers.all()
#         if not headers.exists():
#             return None
#         return {h.key: h.value for h in headers}
    
#     def get_logo(self, obj):
#         request = self.context.get("request")
#         if obj.logo:
#             # If logo is an ImageField, get its URL
#             logo_url = obj.logo.url if hasattr(obj.logo, "url") else f"{settings.MEDIA_URL}{obj.logo}"
#             if request:
#                 return request.build_absolute_uri(logo_url)
#             return logo_url
#         if obj.channel_id:
#             fallback_url = f"http://172.19.0.1/static/tv/logos/{obj.channel_id}.png"
#             return fallback_url
#         return None



# ------------------------------
class ChannelGenreSerializer(serializers.ModelSerializer):
    channels = ChannelSerializer(many=True, read_only=True)

    class Meta:
        model = ChannelGenre
        fields = ["id", "name", "type", "description", "order", "channels"]


class CategorySerializer(serializers.ModelSerializer):
    list = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "list"]

    def get_list(self, obj):
        if obj.category_type == "QUICK_NAV":
            return [
                {"QuickNavigation": QuickNavigationSerializer(item, context=self.context).data}
                for item in obj.quick_navigation.all().order_by("order") 
            ]

        elif obj.category_type == "SEARCH":
            if obj.search_suggestion:
                return [
                    {"Search": SearchSuggestionSerializer(obj.search_suggestion, context=self.context).data}
                ]
            return []

       

        elif obj.category_type == "CHANNEL_GENRE":
            return [
                {"ChannelGenre": ChannelGenreSerializer(item, context=self.context).data}
                for item in obj.channel_genres.all()
            ]


        # elif obj.category_type == "LIVE_TV":  # or "CHANNEL_GENRE"
        #     result = []
        #     for genre in obj.channel_genres.all():
        #         for channel in genre.channels.all():
        #             result.append({
        #                 genre.type: {   # type will be "BigLiveTv" or "LiveTv"
        #                     "id": channel.id,
        #                     "name": channel.name,
                            
        #                     "channel_id": channel.channel_id,
        #                     "description" : channel.description,
        #                        "is_payed" : channel.is_payed,
        #                           "price" : channel.price,
        #                            "order": getattr(channel, "order", 0),
        #                     "favorite": getattr(channel, "favorite", False),
        #                     "timeshift": getattr(channel, "timeshift", False),
        #                     "adult": getattr(channel, "adult", False),
        #                     "ppv": getattr(channel, "ppv", False),
        #                     "ppv_link": getattr(channel, "ppv_link", None),
        #                     "drm_type": getattr(channel, "drm_type", None),
        #                     "status": getattr(channel, "status", None),
        #                     "source_url": getattr(channel, "source_url", None),
        #                     "license_url": getattr(channel, "license_url", None),
                            
        #                      "source_headers": None, 
        #                      "logo": None, 
        #                      "license_headers": None, 
                            
                            
        #                 }
        #             })
        #     return result


        elif obj.category_type == "LIVE_TV":  # or "CHANNEL_GENRE"
            result = []
            profile = self.context.get("profile")
            request = self.context.get("request")

            # Loop through genres linked to this category
            for genre in obj.channel_genres.all():
                # Serialize each channel in the genre
                for channel in genre.channels.all():
                    channel_data = ChannelSerializer(channel, context={"request": request}).data
                    # Optional: mark favorite if you have Favorite model
                    if profile:
                        is_fav = Favorite.objects.filter(profile=profile, channel=channel).exists()
                        channel_data["favorite"] = is_fav
                    else:
                        channel_data["favorite"] = False

                    result.append({
                        genre.type: channel_data  # genre.type is "BigLiveTv" or "LiveTv"
                    })

            return result if result else None
        
        elif obj.category_type == "FAVORITE":
            result = []
            profile = self.context.get("profile")
            request = self.context.get("request")

            if profile:
                # Get top 10 favorite channels
                favorites_qs = Favorite.objects.filter(profile=profile).select_related("channel").order_by("-updated_at")[:10]

                # Serialize only the channel
                for fav in favorites_qs:
                    channel_data = ChannelSerializer(fav.channel, context={"request": request}).data
                    # Mark favorite as True
                    channel_data["favorite"] = True
                    result.append({"BigLiveTv": channel_data})
            if not result:
                return None
            return result
        
               
        elif obj.category_type == "WATCHLIST":
            result = []
            profile = self.context.get("profile")
            request = self.context.get("request")

            if profile:
                # Get top 10 favorite channels
                favorites_qs = WatchHistory.objects.filter(profile=profile).select_related("channel").order_by("-updated_at")[:10]

                # Serialize only the channel
                for fav in favorites_qs:
                    channel_data = ChannelSerializer(fav.channel, context={"request": request}).data
                    # Mark favorite as True
                    channel_data["favorite"] = True
                    result.append({"BigLiveTv": channel_data})
            if not result:
                return None
            return result
        

        

        


