from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from videoflix_videos.models import Video, UserVideoProgress
from videoflix_videos.api.serializers import VideoSerializer, VideoSerializerSingle, UserVideoProgressSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory


class VideoSerializerTestCase(TestCase):
    def setUp(self):
        """Set up test data for serializer testing"""
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.video_file = SimpleUploadedFile("test_video.mp4", b"dummy_video_data", content_type="video/mp4")
        self.thumbnail_file = SimpleUploadedFile("thumbnail.jpg", b"image_data", content_type="image/jpeg")
        
        self.video_no_hls = Video.objects.create(
            title="Test Video No HLS",
            file=self.video_file,
            thumbnail=self.thumbnail_file,
            description="No HLS Playlist",
            genre="Action",
            hls_master_playlist=None
        )
        
        self.video_with_hls = Video.objects.create(
            title="Test Video With HLS",
            file=self.video_file,
            thumbnail=self.thumbnail_file,
            description="HLS Playlist Available",
            genre="Action",
            hls_master_playlist=f"{settings.MEDIA_URL}videos/hls/1/master.m3u8"
        )

        self.progress = UserVideoProgress.objects.create(
            user=self.user,
            video=self.video_with_hls,
            last_viewed_position=50,
            viewed=True
        )

    def test_video_serializer_with_progress(self):
        """Test VideoSerializer returns user progress when authenticated"""
        request = self.factory.get("/")
        request.user = self.user
        serializer = VideoSerializer(instance=self.video_with_hls, context={"request": request})
        data = serializer.data
        expected_progress = UserVideoProgressSerializer(self.progress).data
        self.assertEqual(data["title"], self.video_with_hls.title)
        self.assertEqual(data["user_progress"], expected_progress) 

    def test_video_serializer_without_progress(self):
      """Test VideoSerializer returns None for user_progress when unauthenticated"""
      request = self.factory.get("/")
      request.user = AnonymousUser()
      serializer = VideoSerializer(instance=self.video_with_hls, context={"request": request})
      data = serializer.data
      self.assertEqual(data["title"], self.video_with_hls.title)
      self.assertIsNone(data["user_progress"])


    def test_video_serializer_single_with_hls_and_progress(self):
        """Test VideoSerializerSingle when HLS and user progress is available"""
        request = self.factory.get("/")
        request.user = self.user

        serializer = VideoSerializerSingle(instance=self.video_with_hls, context={"request": request})
        data = serializer.data

        expected_url = f"https://vm.paul-ivan.com{settings.MEDIA_URL}videos/hls/{self.video_with_hls.id}/master.m3u8"
        expected_progress = UserVideoProgressSerializer(self.progress).data

        self.assertEqual(data["title"], self.video_with_hls.title)
        self.assertEqual(data["hls_master_playlist_url"], expected_url)
        self.assertEqual(data["user_progress"], expected_progress)


    def tearDown(self):
        """Cleanup created files"""
        for video in [self.video_no_hls, self.video_with_hls]:
            if video.file and hasattr(video.file, 'path'):
                video.file.delete(save=False)
            if video.thumbnail and hasattr(video.thumbnail, 'path'):
                video.thumbnail.delete(save=False)
