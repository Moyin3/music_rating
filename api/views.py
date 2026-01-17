from django.shortcuts import render
from music_rating.models import Song, Album, Artist, Rating, RateSystem
from music_rating.views import community_rating_for_album, final_album_rating
from .serializers import RateSystemSerializer, SongSerializer, AlbumSerializer, ArtistSerializer, RatingSerializer
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from music_rating.utils.spotify import SpotifyUtils
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
import json
from music_rating.forms import RatingForm

spotify_handler = SpotifyUtils()

class RatingCreateView(CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class RatingDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class AlbumDetailAPIView(APIView):
    def get(self, request, spotify_id) -> Response:
        request.GET = request.GET.copy()
        request.GET["type"] = "albums"
        request.GET["id"] = spotify_id
        response = spotify_handler.spotify_get_id(request)
        
        if isinstance(response, JsonResponse) and response.status_code == 200:
            album_data = response.json()
            rating_system_id = request.session.get("rating_system_id")
            active_rating_system = RateSystem.objects.get(id=rating_system_id) if rating_system_id else RateSystem.objects.first()
            community_rating = community_rating_for_album(album_data, active_rating_system)
            final_rating = final_album_rating(request.user, album_data, active_rating_system)

            user_rating = None
            if request.user.is_authenticated:
                content_type = ContentType.objects.get_for_model(Album)
                user_rating = Rating.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    object_id=spotify_id,
                ).first()

            return Response({
                "album_data": album_data,
                "community_rating": community_rating,
                "final_rating": final_rating,
                "user_rating" : user_rating
            }, status=200)
        elif isinstance(response, JsonResponse) and response.status_code == 404:
            return Response({"error": "Album not found"}, status=404)
        return Response({"detail": "Error fetching album details"}, status=500)
        #TODO: Need to update error handling once I understand how SpotifyUtils works

    
    def post(self, request, spotify_id) -> Response:
        request.GET = request.GET.copy()
        request.GET["type"] = "albums"
        request.GET["id"] = spotify_id
        response = spotify_handler.spotify_get_id(request)

        if isinstance(response, JsonResponse) and response.status_code == 200:
            album_data = response.json()
            album_object, _ = Album.objects.get_or_create(spotify_id=spotify_id)
            for track_id, _ in album_data.get("track_list", []):
                Song.objects.get_or_create(spotify_id=track_id)
            
            """"Need to see how to create a rating, because this is just checking for a rating."""

            
            
            return Response({
                "album_data": album_data,
                "user_rating": RatingSerializer(user_rating).data if user_rating else None,
            }, status = 201)
        elif isinstance(response, JsonResponse) and response.status_code == 404:
            return Response({"error": "Album not found"}, status=404)

        return Response({"detail": "Error fetching album details"}, status=500)
    
    def put(self, request, spotify_id) -> Response:
        request.GET = request.GET.copy()
        request.GET["type"] = "albums"
        request.GET["id"] = spotify_id
        response = spotify_handler.spotify_get_id(request)

        if isinstance(response, JsonResponse) and response.status_code == 200:
            album_data = response.json()
            album_object, _ = Album.objects.get_or_create(spotify_id=spotify_id)
            for track_id, _ in album_data.get("track_list", []):
                Song.objects.get_or_create(spotify_id=track_id)
            
            # This should work if .first gets the latest rating made by the user.
            if request.user.is_authenticated:
                content_type = ContentType.objects.get_for_model(Album)
                user_rating = Rating.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    spotify_id=spotify_id,
                ).first()
            
            return Response({
                "album_data": album_data,
                "user_rating": RatingSerializer(user_rating).data if user_rating else None,
            }, status = 200)
    
    def delete(self, request, spotify_id) -> Response:
        # Only allow deletion if the it's the user's own rating. Need to look back at this.
        if request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Album)
            user_rating = Rating.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=spotify_id,
            ).first()
            if user_rating:
                user_rating.delete()
                return Response({"detail": "Rating deleted"}, status=204)
            else:
                return Response({"error": "Rating not found"}, status=404)
        else:
            return Response({"error": "Authentication required"}, status=401)

class SongDetailAPIView(APIView):
    def get(self, request, spotify_id) -> Response:
        request.GET = request.GET.copy()
        request.GET["type"] = "tracks"
        request.GET["id"] = spotify_id
        response = spotify_handler.spotify_get_id(request)

        if isinstance(response, JsonResponse) and response.status_code == 200:
            song_data = response.json()
            song_object, _ = Song.objects.get_or_create(spotify_id=spotify_id)
            rating_system_id = request.session.get("rating_system_id")
            active_rating_system = RateSystem.objects.get(id=rating_system_id) if rating_system_id else RateSystem.objects.first()
            community_rating = community_rating_for_album(song_data, active_rating_system)
            final_rating = final_album_rating(request.user, song_data, active_rating_system)
            
            user_rating = None
            if request.user.is_authenticated:
                content_type = ContentType.objects.get_for_model(Song)
                user_rating = Rating.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    object_id=spotify_id,
                ).first()
            
            return Response({
                "song_data": song_data,
                "community_rating": community_rating,
                "final_rating": final_rating,
                "user_rating": RatingSerializer(user_rating).data if user_rating else None,
            })
        elif isinstance(response, JsonResponse) and response.status_code == 404:
            return Response({"error": "Song not found"}, status=404)

        return Response({"detail": "Error fetching song details"}, status=500)

    """def post(self, request, spotify_id) -> Response:
        return
        """
class ArtistDetailAPIView(APIView):
    def get(self, request, spotify_id) -> Response:
        request.GET = request.GET.copy()
        request.GET["type"] = "artists"
        request.GET["id"] = spotify_id
        response = spotify_handler.spotify_get_id(request)

        if isinstance(response, JsonResponse) and response.status_code == 200:
            artist_data = response.json()
            artist_object, _ = Artist.objects.get_or_create(spotify_id=spotify_id)
            rating_system_id = request.session.get("rating_system_id")
            active_rating_system = RateSystem.objects.get(id=rating_system_id) if rating_system_id else RateSystem.objects.first()
            community_rating = community_rating_for_album(artist_data, active_rating_system)
            final_rating = final_album_rating(request.user, artist_data, active_rating_system)
            
            user_rating = None
            if request.user.is_authenticated:
                content_type = ContentType.objects.get_for_model(Artist)
                user_rating = Rating.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    object_id=spotify_id,
                ).first()
            
            return Response({
                "artist_data": artist_data,
                "community_rating": community_rating,
                "final_rating": final_rating,
                "user_rating": RatingSerializer(user_rating).data if user_rating else None,
            })
        elif isinstance(response, JsonResponse) and response.status_code == 404:
            return Response({"error": "Artist not found"}, status=404)

        return Response({"detail": "Error fetching artist details"}, status=500)