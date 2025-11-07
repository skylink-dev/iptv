from rest_framework.response import Response
from rest_framework.decorators import api_view
from iptvengine.models import Language
from .models import MovieCategory
from .utils import get_dynamic_movies
from .models import MovieSlider, Movie
from .serializers import MovieSliderSerializer

from django.db.models import Q
@api_view(["GET"])
def movies_with_languages(request):
    # 1️⃣ Fetch all languages (ordered)
    languages = Language.objects.all().order_by("display_order")

    # Format as per Language structure
    language_list = [
        {
            "Language": {
                "id": lang.id,
                "name": lang.name,
                "image": request.build_absolute_uri(lang.image.url) if lang.image else "",
                "langOrder": lang.display_order,
                "tvBanner": request.build_absolute_uri(lang.tv_banner.url) if lang.tv_banner else "",
            }
        }
        for lang in languages
    ]

    # 2️⃣ Fetch movies grouped by category
    movie_data = get_dynamic_movies(limit_per_category=12)

    # Convert movie_data into your desired structure
    movie_categories = [
        {
            "id": idx + 2,  # 2nd category onwards
            "category_id": cat["id"],
            "name": cat["name"],
            "list": [
                {"Movie": movie}
                for movie in [m["Movie"] for m in cat["list"]]
            ],
        }
        for idx, cat in enumerate(movie_data)
    ]

    # 3️⃣ Final combined response
    response_data = {
        "status": 200,
        "message": "Success",
        "data": {
            "categories": [
                {
                    "id": 1,
                    "name": "Explore In Your Language",
                    "list": language_list,
                },
                *movie_categories,  # unpack movie categories
            ]
        },
    }

    return Response(response_data)


@api_view(["GET"])
def MovieslistSliders(request):
    sliders = MovieSlider.objects.filter(is_active=True).order_by("order")
    serializer = MovieSliderSerializer(sliders, many=True)

    response_data = {
        "status": 200,
        "message": "Success",
        "data": serializer.data
    }

    return Response(response_data)



@api_view(["GET"])
def movies_filter(request):
    """
    Fetch movies filtered by category and/or language with pagination.
    Query params:
      - category_id (optional)
      - language_name (optional)
      - page (default 0)
      - size (default 12)
    """
    category_id = request.query_params.get("category_id")
    language_name = request.query_params.get("language_name", "").strip().lower()

    
    page = int(request.query_params.get("page", 0))
    size = int(request.query_params.get("size", 12))

    movies_qs = Movie.objects.all()

    if category_id:
        movies_qs = movies_qs.filter(category__category_id=category_id)

# Use raw SQL to filter JSON array case-insensitively
    if language_name:
        language_name = language_name.lower()
        movies_qs = [m for m in movies_qs if any(lang.lower() == language_name for lang in m.languages)]

    total_items = len(movies_qs)
    start = page * size
    end = start + size
    movies_page = movies_qs[start:end]

    items = [
        {
            "Movie": {
                "id": movie.movie_id,
                "name": movie.name,
                "poster": movie.poster,
                "backdrop": movie.backdrop,
                "languages": movie.languages,
                "quality": movie.quality,
                "rating": movie.rating,
                "isPremiumFirst": movie.isPremiumFirst,
                "isPremium": movie.isPremium,
                "watchingCount": movie.watchingCount,
                "isAdult": movie.isAdult,
                "description": movie.description,
                "trailer": movie.trailer,
                "source": movie.source,
                "isTrailer": movie.isTrailer,
                "is_intent": movie.is_intent,
                "release_year": movie.release_year,
            }
        }
        for movie in movies_page
    ]

    return Response({
        "status": 200,
        "message": "Success",
        "data": {
            "totalItems": total_items,
            "page": page,
            "size": size,
            "items": items
        }
    })