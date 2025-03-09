from django.db import models


class Rating(models.Model):
    score = models.FloatField()


class Song(models.Model):
    song_name = models.CharField(max_length=200)
    no_of_streams = models.IntegerField(null=True)
    no_of_minutes = models.IntegerField(null=True) 
    feat_artists = models.ManyToManyField("Artist", related_name="featured_songs", blank=True)
    rating = models.ForeignKey(Rating, null = True, blank = True)
    optional_writing = models.TextField(blank = True, null=True)
    album = models.ForeignKey("Album", on_delete=models.CASCADE, related_name="songs_album", blank=True, null=True)
    ep = models.ForeignKey("EP", on_delete=models.CASCADE, related_name="songs_ep", blank = True, null = True)
    single = models.ForeignKey("Single", on_delete=models.CASCADE, related_name="songs_single", blank=True, null = True)

    def __str__(self):
        return self.song_name

    
    @property
    def artist_name(self):
        if self.album:
            return self.album.artist_name
        elif self.ep:
            return self.ep.artist_name
        elif self.single:
            return self.single.artist_name
        else:
            return "Unknown"
    
class Album(models.Model):
    album_name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    songs = models.ManyToManyField(Song, related_name="album_songs")
    album_rating = models.ForeignKey(Rating, blank=True, null=True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.album_name

class Single(models.Model):
    single_name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    songs = models.ManyToManyField(Song, related_name="single_songs")
    single_rating = models.ForeignKey(Rating, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.single_name

class EP(models.Model):
    ep_name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    songs = models.ManyToManyField(Song, related_name="ep_songs")
    ep_rating = models.ForeignKey(Rating, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.ep_name

class Artist(models.Model):
    artist_name = models.CharField(max_length=200)
    albums = models.ManyToManyField(Album, blank = True)
    singles = models.ManyToManyField(Single, blank = True)
    eps = models.ManyToManyField(EP, blank = True)
    artist_rating = models.ForeignKey(Rating, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.artist_name

class RateSystem(models.Model):
    artists = models.ManyToManyField(Artist)