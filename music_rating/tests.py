from django.test import TestCase, Client
from .models import Song, Artist, Album, Single, EP, Rating, RateSystem
from unittest.mock import patch
from urllib.parse import urlencode
from django.conf import settings


class ArtistModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(
            spotify_id="12345",
            artist_name="Test Artist",
        )

    def test_artist_str(self):
        self.assertEqual(str(self.artist), "Test Artist")

    def test_artist_fields(self):
        self.assertEqual(self.artist.spotify_id, "12345")
        self.assertEqual(self.artist.artist_name, "Test Artist")

class SongModelTest(TestCase):
    def setUp(self):
        self.artist1 = Artist.objects.create(spotify_id="12345", artist_name="Artist 1")
        self.artist2 = Artist.objects.create(spotify_id="67890", artist_name="Artist 2")
        self.song = Song.objects.create(
            spotify_id="54321",
            song_name="Test Song",
        )
        self.song.artists.add(self.artist1, self.artist2)

    def test_song_str(self):
        self.assertEqual(str(self.song), "Test Song")
    
    def test_song_fields(self):
        self.assertEqual(self.song.spotify_id, "54321")
        self.assertEqual(self.song.song_name, "Test Song")

    def test_song_get_artist_names(self):
        self.assertEqual(self.song.get_artist_names, "Artist 1, Artist 2")

class AlbumModelTest(TestCase):
    def setUp(self):
        self.artist1 = Artist.objects.create(spotify_id="12345", artist_name="Artist 1")
        self.artist2 = Artist.objects.create(spotify_id="67890", artist_name="Artist 2")
        self.album = Album.objects.create(
            spotify_id="11111",
            album_name="Test Album",
        )
        self.album.artists.add(self.artist1, self.artist2)

    def test_album_str(self):
        self.assertEqual(str(self.album), "Test Album")
    
    def test_album_fields(self):
        self.assertEqual(self.album.spotify_id, "11111")
        self.assertEqual(self.album.album_name, "Test Album")

    def test_album_get_artist_names(self):
        self.assertEqual(self.album.get_artist_names, "Artist 1, Artist 2")

class SingleModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(spotify_id="12345", artist_name="Artist 1")
        self.single = Single.objects.create(
            spotify_id="22222",
            single_name="Test Single",
        )
        self.single.artists.add(self.artist)

    def test_single_str(self):
        self.assertEqual(str(self.single), "Test Single")
    
    def test_single_fields(self):
        self.assertEqual(self.single.spotify_id, "22222")
        self.assertEqual(self.single.single_name, "Test Single")

    def test_single_get_artist_names(self):
        self.assertEqual(self.single.get_artist_names, "Artist 1")

class EPModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(spotify_id="12345", artist_name="Artist 1")
        self.ep = EP.objects.create(
            spotify_id="33333",
            ep_name="Test EP",
        )
        self.ep.artists.add(self.artist)

    def test_ep_str(self):
        self.assertEqual(str(self.ep), "Test EP")
    
    def test_ep_fields(self):
        self.assertEqual(self.ep.spotify_id, "33333")
        self.assertEqual(self.ep.ep_name, "Test EP")

    def test_ep_get_artist_names(self):
        self.assertEqual(self.ep.get_artist_names, "Artist 1")
    
class RatingModelTest(TestCase):
    def setUp(self):
        self.rating = Rating.objects.create(score=4.5)

    def test_rating_score(self):
        self.assertEqual(self.rating.score, 4.5)
    
class RateSystemModelTest(TestCase):
    def setUp(self):
        self.rate_system = RateSystem.objects.create(
            name="Custom Rate System",
            description="A custom rating system",
        )

    def test_rate_system_str(self):
        self.assertEqual(str(self.rate_system), "Custom Rate System")

class TemplateViewTests(TestCase):
    def test_entrypage_view(self):
        client = Client()
        response = client.get('/entries/') 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/entrypage.html')
    
    def test_userhome_view(self):
        client = Client()
        response = client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/userhome.html')
    
    def test_artistpage_view(self):
        client = Client()
        response = client.get('/artists/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/artistpage.html')
    
    def test_albumpage_view(self):
        client = Client()
        response = client.get('/albums/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/albumpage.html')
    
    def test_songspage_view(self):
        client = Client()
        response = client.get('/songs/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/songspage.html')
    
    def test_compage_view(self):
        client = Client()
        response = client.get('/community/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/compage.html')
    
    def test_album_detail_view(self):
        testArtist = Artist.objects.create(artist_name="Wizkid")
        testAlbum = Album.objects.create(album_name="Made in Lagos")
        testAlbum.artists.set([testArtist])
        testSong = Song.objects.create(song_name="Grace", album=testAlbum)
        
        client = Client()
        response = client.get(f'/album/{testAlbum.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/album_detail.html')

#TODO: Need to write tests for the updated models page