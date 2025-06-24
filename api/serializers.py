from rest_framework import serializers
from music_rating.models import RateSystem, Rating, Song, UserProfile, Song, Album, Single, EP, Artist

class RateSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateSystem
        fields = ['name', 'description']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'bio']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score', 'user', 'object_id', 'content_type', 'content_object', 'rate_system', 'optional_writing']

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['spotify_id']

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['spotify_id']

class SingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Single
        fields = ['spotify_id']

class EPSerializer(serializers.ModelSerializer):
    class Meta:
        model = EP
        fields = ['spotify_id']

class ArtistSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Artist
        fields = ['spotify_id']