from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



class RateSystem(models.Model):
    description = models.TextField(null=True)
    key = models.CharField(max_length = 50, db_index = True, unique = True)

    def __str__(self):
        return self.key

def default_rate_system():
    return RateSystem.objects.get(key = "explicit")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Rating(models.Model):
    score = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=50, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    rate_system = models.ForeignKey(RateSystem, on_delete=models.PROTECT, default=default_rate_system)
    optional_writing = models.TextField(blank = True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) #Created this incase I want to do something with ratings, in terms of when they were made
    updated_at = models.DateTimeField(auto_now=True) #This allows me to choose the most recent rating for rating helper functions


    class Meta:
         #including the content type in the unique together because unsure of whether Spotify IDs are unique across all content types
        constraints = [
        models.UniqueConstraint(
            fields=["user", "spotify_id", "content_type", "rate_system"],
            name="unique_user_spotify_item_rating"
        ),
        models.CheckConstraint(
                condition=Q(score__gte=0) & Q(score__lte=100),
                name="rating_score_between_0_and_100",
            ),
    ]


class Song(models.Model):
    spotify_id = models.CharField(max_length=50, db_index = True)
    album_spotify_id = models.CharField(max_length=255, db_index = True)
    community_rating = models.IntegerField()

    def recalculateSongCommunityScore(self):
        song_ct = ContentType.objects.get_for_model(Song)
        
        latest_rating_per_user = (
                Rating.objects
                .filter(
                    content_type = song_ct,
                    spotify_id = self.spotify_id,
                    score__isnull = False,
                )
                .order_by("user_id", "-updated_at")
                .distinct("user_id")
            )
        scores = [r.score for r in latest_rating_per_user]
        self.community_rating = int(sum(scores) / len(scores)) if scores else None
        self.save()
        
    
    
class Album(models.Model):
    spotify_id = models.CharField(max_length=50, db_index=True)
    artist_spotify_id = models.CharField(max_length=255, db_index=True)
    community_rating = models.IntegerField()

    def recalculateAlbumCommunityScore(self):
        album_ct = ContentType.objects.get_for_model(Album)
        
        latest_rating_per_user = (
                Rating.objects
                .filter(
                    content_type=album_ct,
                    spotify_id=self.spotify_id,
                    score__isnull=False,
                )
                .order_by("user_id", "-updated_at")
                .distinct("user_id")
            )
        
        scores = [r.score for r in latest_rating_per_user]
        self.community_rating =  int(sum(scores) / len(scores)) if scores else None
        self.save()

class Single(models.Model):
    spotify_id = models.CharField(max_length=50, db_index=True)

class EP(models.Model):
    spotify_id = models.CharField(max_length=50, db_index=True)

class Artist(models.Model):
    spotify_id = models.CharField(max_length=50, db_index=True)
    community_rating = models.IntegerField()

    def recalculateArtistCommunityScore(self):
        artist_ct = ContentType.objects.get_for_model(Artist)
        
        latest_rating_per_user = (
                Rating.objects
                .filter(
                    content_type=artist_ct,
                    spotify_id=self.spotify_id,
                    score__isnull=False,
                )
                .order_by("user_id", "-updated_at")
                .distinct("user_id")
            )
        
        scores = [r.score for r in latest_rating_per_user]
        self.community_rating = int(sum(scores) / len(scores)) if scores else None
        self.save()
