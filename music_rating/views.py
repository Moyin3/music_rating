from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .utils.spotify import SpotifyUtils

from .models import Song, Album, Artist


def entrypage(request):
    template = loader.get_template("music_rating/entrypage.html")
    return HttpResponse(template.render({}, request))


def userhome(request):
    template = loader.get_template("music_rating/userhome.html")
    return HttpResponse(template.render({}, request))


def artistpage(request):
    template = loader.get_template("music_rating/artistpage.html")
    return HttpResponse(template.render({}, request))


def albumpage(request):
    album_list = Album.objects.all()
    return render(request, "music_rating/albumpage.html", {"album_list": album_list})


def songspage(request):
    template = loader.get_template("music_rating/songspage.html")
    return HttpResponse(template.render({}, request))


def compage(request):
    template = loader.get_template("music_rating/compage.html")
    return HttpResponse(template.render({}, request))


def album_detail(request, spotify_id):
    album = get_object_or_404(Album, spotify_id=spotify_id)
    return render(request, 'music_rating/album_detail.html', {'album': album})

def song_detail(request, spotify_id):
    song = get_object_or_404(Song, spotify_id=spotify_id)
    return render(request, 'music_rating/song_detail.html', {'song': song})

def artist_detail(request, spotify_id):
    artist = get_object_or_404(Artist, spotify_id=spotify_id)
    return render(request, 'music_rating/artist_detail.html', {'artist': artist})



### Spotify Search

def spotify_search(request):
    spotify_service = SpotifyUtils()
    return spotify_service.spotify_search(request)

def spotify_id_retrieval(request):
    spotify_service = SpotifyUtils()
    return spotify_service.spotify_get_id(request)

