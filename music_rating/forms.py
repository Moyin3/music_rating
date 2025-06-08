from django import forms
from .models import Song, Album, Single, EP, Artist

class AlbumRatingForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['album_rating', 'optional_writing']
        widgets = {
            'album_rating': forms.NumberInput(attrs={'placeholder': 'Rating'}),
            'optional_writing': forms.Textarea(attrs={'placeholder': 'Optional writing'}),
        }

class SingleRatingForm(forms.ModelForm):
    class Meta:
        model = Single
        fields = ['single_rating', 'optional_writing']
        widgets = {
            'single_rating': forms.NumberInput(attrs={'placeholder': 'Rating'}),
            'optional_writing': forms.Textarea(attrs={'placeholder': 'Optional writing'}),
        }

class SongRatingForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['rating', 'optional_writing']
        widgets = {
            'rating': forms.NumberInput(attrs={'placeholder': 'Rating'}),
            'optional_writing': forms.Textarea(attrs={'placeholder': 'Optional writing'}),
        }
class ArtistRatingForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['artist_rating', 'optional_writing', 'rate_system']
        widgets = {
            'rate_system': forms.Select(attrs={'class': 'form-control'}),
            'artist_rating': forms.NumberInput(attrs={'placeholder': 'Rating'}),
            'optional_writing': forms.Textarea(attrs={'placeholder': 'Optional writing'}),
        }