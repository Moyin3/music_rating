from django import forms
from .models import Rating
from django.contrib.contenttypes.models import ContentType

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'optional_writing', 'rate_system']
        labels = {
            'score': 'Rating',
            'optional_writing': 'Review',
            'rate_system': 'Rating System',
        }
        widgets = {
            'score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1}),
            'optional_writing': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'rate_system': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        # These are passed in manually from the view
        self.content_object = kwargs.pop('content_object', None)
        self.user = kwargs.pop('user', None)
        self.rate_system = kwargs.pop('rate_system', None)
        super().__init__(*args, **kwargs)
        if self.rate_system and self.rate_system.id == 2:
            self.fields['score'].required = False

    
    def save(self, commit=True):
        rating = super().save(commit=False)
        if self.content_object and self.user:
            rating.content_object = self.content_object
            rating.user = self.user
            rating.object_id = self.content_object.spotify_id
            rating.content_type = ContentType.objects.get_for_model(self.content_object)
        if commit:
            rating.save()
        return rating