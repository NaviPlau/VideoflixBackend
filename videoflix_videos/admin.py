from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'hls_master_playlist')
    search_fields = ('title',)
    list_filter = ('uploaded_at',)
