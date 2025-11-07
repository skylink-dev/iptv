# urls.py
from django.urls import path
from . import views

app_name = "admin"

urlpatterns = [
    path('fetch-movies/', views.fetch_movies_view, name='fetch_movies'),
]
