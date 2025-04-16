from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .utils.spotify import SpotifyUtils
import json

from .models import Song, Album, Artist

spotify_handler = SpotifyUtils()

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
    request.GET = request.GET.copy()
    request.GET['type'] = 'albums'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)# Get from cache or API
    if isinstance(response, JsonResponse) and response.status_code == 200:
        data = json.loads(response.content)
        return render(request, 'music_rating/album_detail.html', {'album': data})
    # Handle error cases explicitly
    print("ERROR: Failed to retrieve album details")
    if isinstance(response, JsonResponse):
        return HttpResponse("Error retrieving album details", status=500)
    return HttpResponse("Album not found", status=404)
    

def song_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'tracks'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)# Get from cache or API
    if isinstance(response, JsonResponse) and response.status_code == 200:
        data = json.loads(response.content)
        return render(request, 'music_rating/song_detail.html', {'song': data})
   # Handle error cases explicitly
    print("ERROR: Failed to retrieve album details")
    if isinstance(response, JsonResponse):
        return HttpResponse("Error retrieving song details", status=500)
    return HttpResponse("Album not found", status=404)

def artist_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'artists'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request) # Get from cache or API
    if isinstance(response, JsonResponse) and response.status_code == 200:
        data = json.loads(response.content)
        return render(request, 'music_rating/artist_detail.html', {'artist': data})
   # Handle error cases explicitly
    print("ERROR: Failed to retrieve album details")
    if isinstance(response, JsonResponse):
        return HttpResponse("Error retrieving artist details", status=500)
    return HttpResponse("Album not found", status=404)



### Spotify Search

def spotify_search(request):
    return spotify_handler.spotify_search(request)

def spotify_id_retrieval(request):
    return spotify_handler.spotify_get_id(request)

