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
    song_name = models.CharField(max_length=200)
    no_of_streams = models.IntegerField(null=True)
    no_of_minutes = models.IntegerField(null=True)
    artist_name = models.ManyToManyField("Artist", blank = True)
    feat_artists = models.ManyToManyField("Artist", related_name="featured_songs", blank=True)
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null = True, blank = True)
    optional_writing = models.TextField(blank = True, null=True)
    album = models.ForeignKey("Album", on_delete=models.SET_NULL, related_name="songs_album", blank=True, null=True)
    ep = models.ForeignKey("EP", on_delete=models.SET_NULL, related_name="songs_ep", blank = True, null = True)
    single = models.ForeignKey("Single", on_delete=models.SET_NULL, related_name="songs_single", blank=True, null = True)

    def __str__(self):
        return self.song_name

    
    @property
    def get_artist_name(self):
        if self.album and self.album.artist_name.exists():
            return self.album.artist_name.first().artist_name
        elif self.ep and self.ep.artist_name.exists():
            return self.ep.artist_name.first().artist_name
        elif self.single and self.single.artist_name.exists():
            return self.single.artist_name.first().artist_name
        return "Unknown"
    
class Album(models.Model):
    album_name = models.CharField(max_length=200)
    artist_name = models.ManyToManyField("Artist")
    songs = models.ManyToManyField(Song, related_name="album_songs")
    album_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank=True, null=True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.album_name

class Single(models.Model):
    single_name = models.CharField(max_length=200)
    artist_name = models.ManyToManyField("Artist")
    songs = models.ManyToManyField(Song, related_name="single_songs")
    single_rating = models.ForeignKey(Rating, on_delete = models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.single_name

class EP(models.Model):
    ep_name = models.CharField(max_length=200)
    artist_name = models.ManyToManyField("Artist")
    songs = models.ManyToManyField(Song, related_name="ep_songs")
    ep_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.ep_name

class Artist(models.Model):
    artist_name = models.CharField(max_length=255, null=True) #Had to allow null = True so I could migrate, shouldn't allow artists without names tho.
    albums = models.ManyToManyField(Album, blank = True)
    singles = models.ManyToManyField(Single, blank = True)
    eps = models.ManyToManyField(EP, blank = True)
    rate_system = models.ForeignKey(RateSystem, on_delete=models.CASCADE, default=1)
    artist_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.artist_name
