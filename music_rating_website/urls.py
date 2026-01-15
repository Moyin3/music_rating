from django.contrib import admin
from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path
from music_rating import views
from api.views import AlbumDetailAPIView, SongDetailAPIView, ArtistDetailAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("entries/", views.entrypage, name="entries"),
    path("", views.userhome, name="homepage"),
    path("artists/", views.artistpage, name="artists"),
    path("albums/", views.albumpage, name="albums"),
    path("songs/", views.songspage, name="songs"),
    path("community/", views.compage, name="community"),
    path(
        "album/<str:spotify_id>/", views.album_detail, name="album_detail"
    ),  # Detail page for a single album
    path(
        "spotify-search/", views.spotify_search, name="spotify_search"
    ),  # Return search
    path(
        "song/<str:spotify_id>/", views.song_detail, name="song_detail"
    ),  # Detail page for a single track
    path(
        "artist/<str:spotify_id>/", views.artist_detail, name="artist_detail"
    ),  # Detail page for a single artist
    path("id-retrieval/", views.spotify_id_retrieval, name="id_retrieval"),  # Return id
    path("api/album/<str:spotify_id>", AlbumDetailAPIView.as_view(), name="api_album_detail"),
    path("api/song/<str:spotify_id>", SongDetailAPIView.as_view(), name="api_song_detail"),
    path("api/artist/<str:spotify_id>", ArtistDetailAPIView.as_view(), name="api_artist_detail"),

] + debug_toolbar_urls()
