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
        fields = ['score', 'user', 'content_type','rate_system', 'optional_writing', "spotify_id"]  

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        """Decided to include created, just in case I wanted to do something down 
        the line checking if a new Rating has been created or if it's just an update"""
        rating, created = Rating.objects.update_or_create(
            user = user,
            spotify_id = validated_data["spotify_id"],
            content_type = validated_data["content_type"],
            rate_system = validated_data["rate_system"],
            defaults={
                "score": validated_data["score"],
                # .get function here, because if there isn't any writing, then it will just return None without crashing
                "optional_writing": validated_data.get("optional_writing"),
            },
        )
    
    def validate_score(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Score must be an integer.")

        if not 0 <= value <= 100:
            raise serializers.ValidationError("Score must be between 0 and 100.")

        return value

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
"""
class RatingWriteSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0, max_value=100, required=True)
    rate_system = serializers.IntegerField(required=False)
    optional_writing = serializers.CharField(required=False, allow_blank=True, max_length=1400)

    def __init__(self, *args, **kwargs):
        self.content_object = kwargs.pop("content_object", None)
        self.user = kwargs.pop("user", None)
        self.rate_system = kwargs.pop("rate_system", None)
        super().__init__(*args, **kwargs)
        if self.rate_system and self.rate_system.id == 2:
            self.fields["score"].required = False
"""