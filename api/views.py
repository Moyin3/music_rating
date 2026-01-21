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
from rest_framework.permissions import IsAuthenticated

spotify_handler = SpotifyUtils()

class RatingCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class RatingDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class AlbumDetailAPIView(APIView):
    def get(self, request, spotify_id) -> Response:
        request.GET = request.GET.copy()
        request.GET["type"] = "albums"
        request.GET["spotify_id"] = spotify_id
        
        
        album_data = spotify_handler.spotify_get_id(request)
        
        if not album_data:
            return Response(
                {"detail": "Error fetching album details"},
                status=500
            )

        #This line ensures that when the response is returned if the user is not authenticated user_rating is still simply None.
        user_rating = None


        if request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Album)
            user_rating = (Rating.objects.filter(
                user=request.user,
                content_type=content_type,
                spotify_id=spotify_id,
            )
            .select_related("rate_system")
            .first()
            )
        if user_rating:
            active_rating_system = user_rating.rate_system
        else:
            active_rating_system = RateSystem.objects.get(key = "explicit")
        
        community_rating = community_rating_for_album(album_data, active_rating_system)

        final_rating = None
        if request.user.is_authenticated:
            final_rating = final_album_rating(request.user, album_data, active_rating_system)

        return Response({
            "album_data": album_data,
            "community_rating": community_rating,
            "final_rating": final_rating,
            "user_rating" : user_rating
        }, status=200)
    #TODO: Need to update error handling once I understand how SpotifyUtils works

class SongDetailAPIView(APIView):
    def get(self, request, spotify_id) -> Response:
        request.GET = request.GET.copy()
        request.GET["type"] = "tracks"
        request.GET["spotify_id"] = spotify_id


        song_data = spotify_handler.spotify_get_id(request)

        if not song_data:
            return Response(
                {
                    "detail": "Error fetching song details"
                },
            )
            
            #This line ensures that when the response is returned if the user is not authenticated user_rating is still simply None.
        user_rating = None

        if request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Song)
            user_rating = (Rating.objects.filter(
                user=request.user,
                content_type=content_type,
                spotify_id=spotify_id,
            ).select_related("rate_system")
            .first()
            )
        
        if user_rating:
            active_rating_system = user_rating.rate_system
        else:
            active_rating_system = RateSystem.objects.get(key = "explicit")
        
        community_rating = community_rating_for_album(song_data, active_rating_system)

        final_rating = None
        if request.user.is_authenticated:
            final_rating = final_album_rating(request.user, song_data, active_rating_system)

        return Response({
            "song_data": song_data,
            "community_rating": community_rating,
            "final_rating": final_rating,
            "user_rating": user_rating,
        }, status=200)

    
class ArtistDetailAPIView(APIView):
    def get(self, request, spotify_id) -> Response:
        request.GET = request.GET.copy()
        request.GET["type"] = "artists"
        request.GET["spotify_id"] = spotify_id
        
        
        artist_data = spotify_handler.spotify_get_id(request)
        
        if not artist_data:
            Response({
                "detail": "Error finding Artist details"
            },)

        

            #This line ensures that when the response is returned if the user is not authenticated user_rating is still simply None.
        user_rating = None


        if request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Artist)
            user_rating = (Rating.objects.filter(
                user=request.user,
                content_type=content_type,
                spotify_id=spotify_id,
            ).select_related("rate_system")
            .first()
            )
        
        if user_rating:
            active_rating_system = user_rating.rate_system
        else:
            active_rating_system = RateSystem.objects.get(key = "explicit")

        community_rating = community_rating_for_album(artist_data, active_rating_system)
        
        final_rating = None
        if request.user.is_authenticated:
            final_rating = final_album_rating(request.user, artist_data, active_rating_system)


        return Response({
            "artist_data": artist_data,
            "community_rating": community_rating,
            "final_rating": final_rating,
            "user_rating": user_rating,
        }, status=200)