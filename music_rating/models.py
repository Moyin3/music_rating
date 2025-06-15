from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class RateSystem(models.Model):
    name = models.CharField(max_length=255, default = 'OG')
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Rating(models.Model):
    score = models.IntegerField(null=True, blank=True)  # This is to allow for null values, for the second rating system
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # Nulls for a temporary fix, to enable migrations without breaking existing data
    object_id = models.CharField(max_length=50, null = True) # Nulls for a temporary fix, to enable migrations without breaking existing data
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True) # Nulls for a temporary fix, to enable migrations without breaking existing data
    content_object = GenericForeignKey('content_type', 'object_id')
    rate_system = models.ForeignKey(RateSystem, on_delete=models.CASCADE, default=1)
    optional_writing = models.TextField(blank = True, null=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')


class Song(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)
    
    
class Album(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)

class Single(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)

class EP(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)

class Artist(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)
