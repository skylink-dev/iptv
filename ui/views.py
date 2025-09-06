from django.shortcuts import render
from django.shortcuts import redirect
from .models import JazzminSettings
# Create your views here.

def reset_theme(request):
    JazzminSettings.objects.all().delete()
    return redirect('/admin/')