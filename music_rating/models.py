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
    score = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')


class Song(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)
    optional_writing = models.TextField(blank = True, null=True)
    
class Album(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)
    optional_writing = models.TextField(blank = True, null = True)
    rate_system = models.ForeignKey(RateSystem, on_delete=models.CASCADE, default=1)

class Single(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)
    optional_writing = models.TextField(blank = True, null = True)

class EP(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)
    optional_writing = models.TextField(blank = True, null = True)

class Artist(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="", primary_key=True)
    rate_system = models.ForeignKey(RateSystem, on_delete=models.CASCADE, default=1)
    optional_writing = models.TextField(blank = True, null = True)
