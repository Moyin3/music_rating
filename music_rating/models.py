from django.db import models


class Rating(models.Model):
    score = models.FloatField()

class Song(models.Model):
    song_name = models.CharField(max_length=200)
    no_of_streams = models.IntegerField()
    no_of_minutes = models.IntegerField() 
    feat_name = models.CharField(max_length=200)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    optional_writing = models.TextField()
    artist_name = models.CharField(max_length=200)

    def __str__(self):
        return self.song_name

class Album(models.Model):
    album_name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    songs = models.ManyToManyField(Song)
    album_rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    optional_writing = models.TextField()

    def __str__(self):
        return self.album_name

class Single(models.Model):
    single_name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    songs = models.ManyToManyField(Song)
    single_rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    optional_writing = models.TextField()

    def __str__(self):
        return self.single_name

class EP(models.Model):
    ep_name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    songs = models.ManyToManyField(Song)
    ep_rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    optional_writing = models.TextField()

    def __str__(self):
        return self.ep_name

class Artist(models.Model):
    artist_name = models.CharField(max_length=200)
    albums = models.ManyToManyField(Album)
    singles = models.ManyToManyField(Single)
    eps = models.ManyToManyField(EP)
    optional_writing = models.TextField()

    def __str__(self):
        return self.artist_name

class RateSystem(models.Model):
    artists = models.ManyToManyField(Artist)