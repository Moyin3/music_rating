from django.contrib import admin
from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path, include, re_path
from api.views import (AlbumDetailAPIView, SongDetailAPIView, ArtistDetailAPIView, 
                       RatingDetailView, RatingCreateView, SpotifySearchView, RatingListView, UsernameSearchView, GoogleLogin)
from django.views.generic import TemplateView
from django.shortcuts import redirect

def redirect_to_frontend_reset(request, uidb64, token):
    return redirect(f"http://127.0.0.1:5173/reset-password/{uidb64}/{token}/")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/album/<str:spotify_id>", AlbumDetailAPIView.as_view(), name="api_album_detail"),
    path("api/song/<str:spotify_id>", SongDetailAPIView.as_view(), name="api_song_detail"),
    path("api/artist/<str:spotify_id>", ArtistDetailAPIView.as_view(), name="api_artist_detail"),
    path("api/ratings/<int:pk>", RatingDetailView.as_view(), name = "ratings-RUD"),
    path("api/ratings/", RatingCreateView.as_view(), name = "ratings-create"),
    path("api/dj-rest-auth/", include("dj_rest_auth.urls")),
    path("api/dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/search/", SpotifySearchView.as_view(), name = "search"),
    path("api/search/users/", UsernameSearchView.as_view(), name = "userSearch"),
    path("api/reviews/", RatingListView.as_view(), name= "rating-list"),
    re_path(r'^api/auth/account-confirm-email/(?P<key>[-:\w]+)/$',
            TemplateView.as_view(),
            name = "account_confirm_email",
    ),
    # This path is being added so that the password reset email can be sent, seems
    # dj rest auth has an issue where it isn't trying to reverse the correct name, 
    # it reverses password_reset_confirm instead of rest_password_reset_confirm which
    # dj rest auth have written"""
    path(
        "api/dj-rest-auth/password/reset/confirm/<uidb64>/<token>/",
        redirect_to_frontend_reset,
        name = "password_reset_confirm"
    ),
    path('api/dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    ] + debug_toolbar_urls()
