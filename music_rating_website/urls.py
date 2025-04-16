"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path
from music_rating import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("entries/", views.entrypage, name="entries"),
    path("", views.userhome, name = "homepage"),
    path("artists/", views.artistpage, name = "artists"),
    path("albums/", views.albumpage, name = "albums"),
    path("songs/", views.songspage, name = "songs"),
    path("community/", views.compage, name = "community"),
    path('album/<str:spotify_id>/', views.album_detail, name='album_detail'),  # Detail page for a single album
    path('spotify-search/', views.spotify_search, name='spotify_search'), # Return search
    path('song/<str:spotify_id>/', views.song_detail, name='song_detail'),  # Detail page for a single track
    path('artist/<str:spotify_id>/', views.artist_detail, name='artist_detail'),  # Detail page for a single artist
    path('id-retrieval/', views.spotify_id_retrieval, name='id_retrieval'), # Return id
] + debug_toolbar_urls()
