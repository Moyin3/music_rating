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
    song_name = models.CharField(max_length=200)
    artists = models.ManyToManyField("Artist", blank = True)
    feat_artists = models.ManyToManyField("Artist", related_name="featured_songs", blank=True)
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null = True, blank = True)
    optional_writing = models.TextField(blank = True, null=True)
    album = models.ForeignKey("Album", on_delete=models.SET_NULL, related_name="songs_album", blank=True, null=True)
    ep = models.ForeignKey("EP", on_delete=models.SET_NULL, related_name="songs_ep", blank = True, null = True)
    single = models.ForeignKey("Single", on_delete=models.SET_NULL, related_name="songs_single", blank=True, null = True)

    def __str__(self):
        return self.song_name

    @property
    def get_artist_names(self):
        # Return a comma-separated list of artist names
        return ", ".join([artist.artist_name for artist in self.artists.all()])
    
class Album(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    album_name = models.CharField(max_length=200)
    artists = models.ManyToManyField("Artist")
    songs = models.ManyToManyField(Song, related_name="album_songs")
    album_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank=True, null=True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.album_name

    @property
    def get_artist_names(self):
        # Return a comma-separated list of artist names
        return ", ".join([artist.artist_name for artist in self.artists.all()])

class Single(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    single_name = models.CharField(max_length=200)
    artists = models.ManyToManyField("Artist")
    songs = models.ManyToManyField(Song, related_name="single_songs")
    single_rating = models.ForeignKey(Rating, on_delete = models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.single_name

    @property
    def get_artist_names(self):
        # Return a comma-separated list of artist names
        return ", ".join([artist.artist_name for artist in self.artists.all()])

class EP(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    ep_name = models.CharField(max_length=200)
    artists = models.ManyToManyField("Artist")
    songs = models.ManyToManyField(Song, related_name="ep_songs")
    ep_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.ep_name

    @property
    def get_artist_names(self):
        # Return a comma-separated list of artist names
        return ", ".join([artist.artist_name for artist in self.artists.all()])

class Artist(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True, db_index=True, default="")
    artist_name = models.CharField(max_length=255, null=False)
    rate_system = models.ForeignKey(RateSystem, on_delete=models.CASCADE, default=1)
    artist_rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, blank = True, null = True)
    optional_writing = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.artist_name
