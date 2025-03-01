from django.contrib import admin
from .models import Artist, Album, Song, Rating, EP, Single, RateSystem

admin.site.register([Artist, Rating, EP, Single])

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    exclude = ('no_of_minutes', 'no_of_streams', 'rating', 'optional_writing')
    search_fields = ['song_name']
    filter_horizontal = ['feat_artists']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "feat_artists":
            kwargs["queryset"] = db_field.related_model.objects.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

class SongInline(admin.TabularInline):  # You can also use StackedInline
    model = Song
    extra = 1  # Number of empty song forms shown (optional)
    fields = ('song_name', 'no_of_streams', 'no_of_minutes', 'feat_artists', 'rating', 'optional_writing')

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    inlines = [SongInline]
    filter_horizontal = ['songs']