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