from django.test import TestCase
from .models import Song, Artist, Album, Single, EP


class AlbumModelTests(TestCase):
    def test_song_name_and_artist(self):
        testArtist = Artist.objects.create(artist_name="Wizkid")
        testSong = Song.objects.create(song_name="Fever")
        testSong.artist_name.set([testArtist])

        self.assertEqual(testSong.song_name, "Fever")
        self.assertEqual(testSong.artist_name.first().artist_name, "Wizkid")
