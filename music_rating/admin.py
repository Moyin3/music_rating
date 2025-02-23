from django.contrib import admin
from .models import Artist, Album, Song, Rating, EP, Single, RateSystem

admin.site.register([Artist, Album, Song, Rating, EP, Single])
