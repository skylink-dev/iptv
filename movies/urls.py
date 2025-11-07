from django.urls import path
from .views import movies_with_languages, MovieslistSliders, movies_filter

urlpatterns = [
    path("list/", movies_with_languages, name="movie-list"),
    path("sliders/", MovieslistSliders, name="movieslist-sliders"),
    path("filter/", movies_filter,  name="movieslist-filter"),
]
