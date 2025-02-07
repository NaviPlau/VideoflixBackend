from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videoflix_videos.models import Video
from ..tasks import convert_to_hls
from .serializers import VideoSerializer 

class UploadVideoView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save()
            task = convert_to_hls.delay(video.id)
            return Response({
                'message': 'Video uploaded successfully and conversion started.',
                'video_id': video.id,
                'task_id': task.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class VideoListView(APIView):
    def get(self, request, *args, **kwargs):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
