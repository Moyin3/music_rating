from django.db import models
from django.db.models import Q, Avg
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)



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

@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):
    # using if created because I only want to create UserProfile 
    # object when a new user is created, not when an existing user is saved or
    # updated.
    if created:
        UserProfile.objects.create(user = instance)

class Rating(models.Model):
    name = models.CharField()
    score = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=50, db_index=True)
    album_spotify_id = models.CharField(max_length=255, db_index = True, null = True)
    artist_spotify_id = models.CharField(max_length=255, db_index = True, null = True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    rate_system = models.ForeignKey(RateSystem, on_delete=models.PROTECT, default=default_rate_system)
    optional_writing = models.TextField(blank = True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) #Created this incase I want to do something with ratings, in terms of when they were made
    updated_at = models.DateTimeField(auto_now=True) #This allows me to choose the most recent rating for rating helper functions


    class Meta:
         #including the content type in the unique together because unsure of whether Spotify IDs are unique across all content types
        constraints = [
        models.UniqueConstraint(
            fields=["user", "spotify_id", "content_type", "rate_system", "album_spotify_id", "artist_spotify_id"],
            name="unique_user_spotify_item_rating"
        ),
        models.CheckConstraint(
                condition=Q(score__gte=0) & Q(score__lte=100),
                name="rating_score_between_0_and_100",
            ),
    ]

    def save(self, *args, **kwargs):
        super(Rating, self).save(*args, **kwargs)
        latest_rating_per_user = (
            Rating.objects.filter(
                content_type = self.content_type,
                spotify_id = self.spotify_id,
                score__isnull = False,
            )
            .order_by("user_id", "-updated_at")
            .distinct("user_id")
        )
        song_ct = ContentType.objects.get_for_model(Song)
        album_ct = ContentType.objects.get_for_model(Album)
        artist_ct = ContentType.objects.get_for_model(Artist)
        rate_system = RateSystem.objects.get(key="average")
        scores = [r.score for r in latest_rating_per_user]
        community_rating = int(sum(scores) / len(scores)) if scores else None

        rating_object = None
        if self.content_type.model_class() == Song:
            rating_object, _ = self.content_type.model_class().objects.get_or_create(spotify_id = self.spotify_id, album_spotify_id = self.album_spotify_id)
            #Everything below is essentially just a copy of the helper function, I don't like this
            #TODO: refactor later
            album_rating_object = (Rating.objects.filter(spotify_id = rating_object.album_spotify_id).order_by("-updated_at")).first()
            if album_rating_object and album_rating_object.rate_system.key == "average":
                songs = Song.objects.filter(album_spotify_id=album_rating_object.spotify_id)
                if not songs.exists():
                    logger.error("Can't find any songs in this album")
                    return 0
                ratings = Rating.objects.filter(
                        user=self.user,
                        content_type=song_ct,
                        spotify_id__in=songs.values_list("spotify_id", flat=True),
                    )
                
                if not ratings.exists():
                    logger.error("Ratings don't exist for this album to be averaged")
                    return 0
            
                avg_score = int(ratings.aggregate(avg=Avg("score"))["avg"])
            
                Rating.objects.filter(
                    user=self.user,
                    content_type=album_ct,
                    spotify_id=album_rating_object.spotify_id,
                    rate_system=rate_system
                ).update(score = avg_score)

                latest_rating_per_user = (
                            Rating.objects.filter(
                                content_type = album_ct,
                                spotify_id = album_rating_object.spotify_id,
                                score__isnull = False,
                            )
                            .order_by("user_id", "-updated_at")
                            .distinct("user_id")
                        )
                
                scores = [r.score for r in latest_rating_per_user]
                community_rating = int(sum(scores) / len(scores)) if scores else None

                Album.objects.filter(
                    spotify_id=album_rating_object.spotify_id
                ).update(community_rating = community_rating)

        elif self.content_type.model_class() == Album:
            rating_object, _ = self.content_type.model_class().objects.get_or_create(spotify_id = self.spotify_id, artist_spotify_id = self.artist_spotify_id)
            #TODO: Refactor this nonsense too
            artist_rating_object = (Rating.objects.filter(spotify_id = rating_object.artist_spotify_id).order_by("-updated_at")).first()
            if artist_rating_object and artist_rating_object.rate_system.key == "average":
                albums = Album.objects.filter(artist_spotify_id=artist_rating_object.spotify_id)
                if not albums.exists():
                    return 0
                ratings = Rating.objects.filter(
                        user=self.user,
                        content_type=album_ct,
                        spotify_id__in=albums.values_list("spotify_id", flat=True)
                    ) 
                if not ratings.exists():
                    return 0
            
                avg_score = int(ratings.aggregate(avg=Avg("score"))["avg"])
            
                Rating.objects.filter(
                    user=self.user,
                    content_type=artist_ct,
                    spotify_id=artist_rating_object.spotify_id,
                    rate_system=rate_system,
                ).update(score = avg_score)

                latest_rating_per_user = (
                    Rating.objects.filter(
                        content_type = artist_ct,
                        spotify_id = artist_rating_object.spotify_id,
                        score__isnull = False,
                    )
                    .order_by("user_id", "-updated_at")
                    .distinct("user_id")
                )
                                
                scores = [r.score for r in latest_rating_per_user]
                community_rating = int(sum(scores) / len(scores)) if scores else None

                Artist.objects.filter(
                    spotify_id=artist_rating_object.spotify_id
                ).update(community_rating = community_rating)
        else:
            rating_object, _ = self.content_type.model_class().objects.get_or_create(spotify_id = self.spotify_id)

        rating_object.community_rating = community_rating
        rating_object.save()

class Song(models.Model):
    spotify_id = models.CharField(max_length=50, db_index = True)
    album_spotify_id = models.CharField(max_length=255, db_index = True, null = True)
    community_rating = models.IntegerField(null = True)
        
    
    
class Album(models.Model):
    spotify_id = models.CharField(max_length=50, db_index=True)
    artist_spotify_id = models.CharField(max_length=255, db_index=True, null = True)
    community_rating = models.IntegerField(null = True)


class Single(models.Model):
    spotify_id = models.CharField(max_length=50, db_index=True)

class EP(models.Model):
    spotify_id = models.CharField(max_length=50, db_index=True)

class Artist(models.Model):
    spotify_id = models.CharField(max_length=50, db_index=True)
    community_rating = models.IntegerField(null = True)
