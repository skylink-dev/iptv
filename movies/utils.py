import requests
from .models import MovieCategory, Movie

API_URL = "https://api2.ottplay.com/api/partnerfeed-service/v1/partner/widget-list?seo_url=partner/skylink-fibernet/7b9bb903a757&t=463747"

def fetch_and_save_movies():

    #Movie.objects.all().delete()
    response = requests.get(API_URL, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    widgets = data.get("widgets", [])
    updated_count = 0

    for widget in widgets:
        category_name = widget.get("name", "Unknown Category")
        category_id = widget.get("id")  # API category ID

        # Update or create category using API ID
        category, _ = MovieCategory.objects.update_or_create(
            category_id=category_id,
            defaults={"name": category_name}
        )
        
        for item in widget.get("data", []):
            languages = [item.get("language")] if item.get("language") else item.get("languages", [])

            # Update or create movie using API movie_id
            movie, _ = Movie.objects.update_or_create(
                movie_id=item.get("id"),
                defaults={
                    "name": item.get("name"),
                    "category": category,
                    "poster": item.get("poster_image") or "",
                    "backdrop": item.get("backdrop_image") or "",
                    "languages": languages,
                    "quality": "HD",
                    "rating": str(item.get("ottplay_rating") or 0),
                    "isPremiumFirst": False,
                    "isPremium": False,
                    "watchingCount": "0",
                    "isAdult": False,
                    "description": item.get("genre") or "",
                    "trailer": "",  # trailer should come empty
                    "source": item.get("ottplay_url") or "",
                    "isTrailer": False,
                    "is_intent": True,  # default value
                    "release_year": item.get("release_year"),
                }
            )
            updated_count += 1

    return updated_count


from movies.models import MovieCategory
def get_dynamic_movies(limit_per_category=12, id_offset=10001):
    """
    Fetch all movie categories and their movies, return in API-ready format.
    Limits the number of movies per category to `limit_per_category`.
    """
    dynamic_movies = []
    movie_categories = MovieCategory.objects.prefetch_related("movies").all()
    
    for cat in movie_categories:
        movies_qs = cat.movies.all()[:limit_per_category]  # limit to 12 movies per category
        dynamic_movies.append({
            "id": cat.category_id,
            "name": cat.name,
            "list": [
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
                        "trailer": movie.trailer,  # will be empty
                        "source": movie.source,
                        "isTrailer": movie.isTrailer,
                        "is_intent": movie.is_intent,
                        "release_year": movie.release_year,
                    }
                } for movie in movies_qs
            ]
        })
    
    return dynamic_movies
