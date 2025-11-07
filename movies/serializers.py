from rest_framework import serializers
from .models import MovieSlider

class MovieSliderSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    poster = serializers.SerializerMethodField()
    backdrop = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    quality = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    isPremiumFirst = serializers.SerializerMethodField()
    isPremium = serializers.SerializerMethodField()
    watchingCount = serializers.SerializerMethodField()
    isAdult = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    trailer = serializers.SerializerMethodField()
    isTrailer = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()   
    is_intent = serializers.SerializerMethodField()  

    class Meta:
        model = MovieSlider
        fields = [
            "id", "name", "poster", "backdrop", "languages", "quality",
            "rating", "isPremiumFirst", "isPremium", "watchingCount",
            "isAdult", "description", "trailer", "isTrailer",   "source", "is_intent" 
        ]

    def get_id(self, obj):
        return obj.movie.id if obj.movie else None

    def get_name(self, obj):
        return obj.movie.name if obj.movie else ""

    def get_poster(self, obj):
        return obj.movie.poster if obj.movie else ""

    def get_backdrop(self, obj):
        return obj.movie.backdrop if obj.movie else ""

    def get_languages(self, obj):
        return obj.movie.languages if obj.movie else []

    def get_quality(self, obj):
        return obj.movie.quality if obj.movie else ""

    def get_rating(self, obj):
        return obj.movie.rating if obj.movie else ""

    def get_isPremiumFirst(self, obj):
        return obj.movie.isPremiumFirst if obj.movie else False

    def get_isPremium(self, obj):
        return obj.movie.isPremium if obj.movie else False

    def get_watchingCount(self, obj):
        return obj.movie.watchingCount if obj.movie else "0"

    def get_isAdult(self, obj):
        return obj.movie.isAdult if obj.movie else False

    def get_description(self, obj):
        return obj.movie.description if obj.movie else ""

    def get_trailer(self, obj):
        return obj.movie.trailer if obj.movie else ""

    def get_isTrailer(self, obj):
        return obj.movie.isTrailer if obj.movie else False
    def get_source(self, obj):
        return obj.movie.source if obj.movie else ""

    def get_is_intent(self, obj):
        return obj.movie.is_intent if obj.movie else False