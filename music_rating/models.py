from django.db import models


"""Unsure about this but chat said could come in handy for consistency across models
"""
class RateSystem(models.Model):
    name = models.CharField(max_length=255, default = 'OG')
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

class Rating(models.Model):
    score = models.FloatField()


class Song(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null = True, blank = True)
    optional_writing = models.TextField(blank = True, null=True)
    
class Album(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    album_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank=True, null=True)
    optional_writing = models.TextField(blank = True, null = True)

class Single(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    single_rating = models.ForeignKey(Rating, on_delete = models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

class EP(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    ep_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

class Artist(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    rate_system = models.ForeignKey(RateSystem, on_delete=models.CASCADE, default=1)
    artist_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)
