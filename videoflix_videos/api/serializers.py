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
        fields = ['title', 'file', 'thumbnail', 'description', 'hls_master_playlist', 'uploaded_at', 'user_progress', 'id', 'genre']

    def get_user_progress(self, obj):
        """
        Return the user's progress for the given video as a serialized UserVideoProgress, or None if the user is not authenticated or no progress is found.
        """
        request = self.context.get('request')
        if request:
            print(f"Request user: {request.user}, Authenticated: {request.user.is_authenticated}")
        if request and request.user.is_authenticated:
            progress = UserVideoProgress.objects.filter(user=request.user, video=obj).first()
            print(f"Progress found: {progress}")
            if progress:
                return UserVideoProgressSerializer(progress).data
        return None
    
    
class VideoSerializerSingle(serializers.ModelSerializer):
    user_progress = serializers.SerializerMethodField()
    hls_master_playlist_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['title', 'file', 'thumbnail', 'description', 'hls_master_playlist_url', 'uploaded_at', 'user_progress', 'id', 'genre', 'user_progress'] 

    def get_hls_master_playlist_url(self, obj):
        """
        Return the URL of the HLS master playlist for the given video, or None if no HLS version of the video exists.
        
        The URL is constructed by concatenating the MEDIA_URL setting with the video ID and the path to the master.m3u8 file.
        """
        
        if obj.hls_master_playlist:
            return f"http://127.0.0.1:8000{settings.MEDIA_URL}videos/hls/{obj.id}/master.m3u8"
        return None

    def get_user_progress(self, obj):
        """
        Retrieve the user's progress for the specified video.

        This method checks if the request context contains an authenticated user.
        If the user is authenticated and has progress related to the given video, 
        it returns the serialized progress data. If no progress is found or the 
        user is not authenticated, it returns None.

        Args:
            obj (Video): The video object for which to retrieve user progress.

        Returns:
            dict or None: Serialized user progress data if available, otherwise None.
        """

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            progress = UserVideoProgress.objects.filter(user=request.user, video=obj).first()
            if progress:
                return UserVideoProgressSerializer(progress).data
        return None


class UserVideoProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVideoProgress
        fields = ['last_viewed_position', 'viewed',]