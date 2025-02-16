from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videoflix_videos.models import Video, UserVideoProgress
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..tasks import convert_to_hls
from .serializers import VideoSerializer, VideoSerializerSingle, UserVideoProgressSerializer
from django.shortcuts import get_object_or_404

class UploadVideoView(APIView):
    permission_classes= [AllowAny]
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
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class SingleVideoView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, video_id, *args, **kwargs):
        video = get_object_or_404(Video, id=video_id)
        serializer = VideoSerializerSingle(video, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class VideoProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, video_id):
        try:
            progress, created = UserVideoProgress.objects.get_or_create(
                user=request.user,
                video_id=video_id
            )
            serializer = UserVideoProgressSerializer(progress, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Video.DoesNotExist:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)