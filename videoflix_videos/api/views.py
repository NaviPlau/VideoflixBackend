from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videoflix_videos.models import Video, UserVideoProgress
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from ..tasks import convert_to_hls
from .serializers import VideoSerializer, VideoSerializerSingle, UserVideoProgressSerializer
from django.shortcuts import get_object_or_404

class UploadVideoView(APIView):
    permission_classes= [IsAdminUser]
    def post(self, request, *args, **kwargs):
        """
        Upload a new video.
        This API endpoint takes a POST request with the following fields:
        - title (string): The title of the video.
        - file (file): The video file to upload.
        - thumbnail (file): The video thumbnail to upload.
        - description (string): The description of the video.
        - genre (string): The genre of the video.
        Returns a JSON response with the following keys:
        - message (string): A message indicating that the video was uploaded successfully and conversion has started.
        - video_id (int): The ID of the video that was just uploaded.
        - task_id (string): The Celery task ID for the HLS conversion task.
        """
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
        """
        Retrieve a list of all available videos.

        This API endpoint requires authentication and returns a JSON response
        containing a list of all videos available in the system. Each video is
        serialized using the VideoSerializer, which includes fields such as
        title, file, thumbnail, description, and genre.

        Returns:
            Response: A JSON response with serialized video data and HTTP 200 status.
        """
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class SingleVideoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, video_id, *args, **kwargs):
        """
        Retrieve a single video by its ID.

        This API endpoint requires authentication and returns a JSON response
        containing the video with the specified ID. The video is serialized
        using the VideoSerializerSingle, which includes fields such as title,
        file, thumbnail, description, and genre.

        Args:
            video_id (int): The ID of the video to retrieve.

        Returns:
            Response: A JSON response with serialized video data and HTTP 200 status.
        """
        video = get_object_or_404(Video, id=video_id)
        serializer = VideoSerializerSingle(video, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class VideoProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, video_id):
        """
        Update or create the user's video progress for a specific video.

        This API endpoint requires authentication and allows the user to update
        the progress of a video they are watching. The progress is represented by
        fields such as 'last_viewed_position' and 'viewed' status.

        Args:
            request (Request): The HTTP request object containing user data and progress update data.
            video_id (int): The ID of the video for which the user's progress is being updated.

        Returns:
            Response: A JSON response with the updated progress data and HTTP 200 status if successful,
            or a JSON response with error details and the appropriate HTTP status code if an error occurs.
        """

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