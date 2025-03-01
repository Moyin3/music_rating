from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Song, Album

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
    return render(request, "music_rating/albumpage.html", {'album_list': album_list})

def songspage(request):
    template = loader.get_template("music_rating/songspage.html")
    return HttpResponse(template.render({}, request))

def compage(request):
    template = loader.get_template("music_rating/compage.html")
    return HttpResponse(template.render({}, request))

def album_detail(request, album_id):
    album = Album.objects.get(id=album_id)
    return render(request, 'music_rating/album_detail.html', {'album': album})