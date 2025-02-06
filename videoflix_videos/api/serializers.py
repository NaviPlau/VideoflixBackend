from rest_framework import serializers
from videoflix_videos.models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['title', 'file', 'thumbnail', 'description']