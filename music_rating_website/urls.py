from django.contrib import admin
from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path, include
from api.views import (AlbumDetailAPIView, SongDetailAPIView, ArtistDetailAPIView, 
                       RatingDetailView, RatingCreateView, SpotifySearchView, DisplayTracksAndDiscographyView)
from dj_rest_auth.registration.views import VerifyEmailView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/album/<str:spotify_id>", AlbumDetailAPIView.as_view(), name="api_album_detail"),
    path("api/song/<str:spotify_id>", SongDetailAPIView.as_view(), name="api_song_detail"),
    path("api/artist/<str:spotify_id>", ArtistDetailAPIView.as_view(), name="api_artist_detail"),
    path("api/ratings/<int:pk>", RatingDetailView.as_view(), name = "ratings-RUD"),
    path("api/ratings/", RatingCreateView.as_view(), name = "ratings-create"),
    path("api/dj-rest-auth/", include("dj_rest_auth.urls")),
    path("api/dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/dj-rest-auth/registration/account-confirm-email/", VerifyEmailView.as_view(), name = "account_email_verification_sent"),
    path("api/search/", SpotifySearchView.as_view(), name = "search"),
    path("api/discography/", DisplayTracksAndDiscographyView.as_view(), name = "discography")
    
    ] + debug_toolbar_urls()
