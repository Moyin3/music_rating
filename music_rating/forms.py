from django import forms
from .models import Rating
from django.contrib.contenttypes.models import ContentType

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1}),
        }

    def __init__(self, *args, **kwargs):
        # These are passed in manually from the view
        self.content_object = kwargs.pop('content_object', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        rating = super().save(commit=False)
        if self.content_object and self.user:
            rating.content_object = self.content_object
            rating.user = self.user
            rating.object_id = self.content_object.spotify_id
            rating.content_type = ContentType.objects.get_for_model(self.content_object)
            print(f"Set on Rating: object_id={rating.object_id}, content_type={rating.content_type}")
        if commit:
            rating.save()
        return rating