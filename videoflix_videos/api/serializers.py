from rest_framework import serializers
from django.conf import settings
from videoflix_videos.models import Video, UserVideoProgress

class UserVideoProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVideoProgress
        fields = ['last_viewed_position', 'viewed', 'last_viewed_at']

class VideoSerializer(serializers.ModelSerializer):
    user_progress = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['title', 'file', 'thumbnail', 'description', 'hls_master_playlist', 'uploaded_at', 'user_progress', 'id']

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            progress = UserVideoProgress.objects.filter(user=request.user, video=obj).first()
            if progress:
                return UserVideoProgressSerializer(progress).data
        return None 
    
    
class VideoSerializerSingle(serializers.ModelSerializer):
    user_progress = serializers.SerializerMethodField()
    hls_master_playlist_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['title', 'file', 'thumbnail', 'description', 'hls_master_playlist_url', 'uploaded_at', 'user_progress']

    def get_hls_master_playlist_url(self, obj):
        if obj.hls_master_playlist:
            return f"http://127.0.0.1:8000{settings.MEDIA_URL}videos/hls/{obj.id}/master.m3u8"
        return None

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            progress = UserVideoProgress.objects.filter(user=request.user, video=obj).first()
            if progress:
                return UserVideoProgressSerializer(progress).data
        return None
