from django.test import TestCase
from django.contrib.auth.models import User
from videoflix_videos.models import Video, UserVideoProgress
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class VideoModelTestCase(TestCase):
    def setUp(self):
        """Set up test data for the models"""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.video_file = SimpleUploadedFile("test_video.mp4", b"dummy_video_data", content_type="video/mp4")
        self.thumbnail_file = SimpleUploadedFile("thumbnail.jpg", b"image_data", content_type="image/jpeg")

        self.video = Video.objects.create(
            title="Test Video",
            file=self.video_file,
            thumbnail=self.thumbnail_file,
            description="This is a test video",
            genre="Action"
        )

    def test_video_creation(self):
        """Test that a video is created correctly"""
        self.assertEqual(self.video.title, "Test Video")
        self.assertTrue(self.video.file)
        self.assertTrue(self.video.thumbnail)
        self.assertEqual(self.video.genre, "Action")

    def test_video_string_representation(self):
        """Test string representation of the video model"""
        self.assertEqual(str(self.video), "Test Video")

    def test_user_video_progress_creation(self):
        """Test creating a UserVideoProgress record"""
        progress = UserVideoProgress.objects.create(
            user=self.user,
            video=self.video,
            last_viewed_position=120,
            viewed=True
        )
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.video, self.video)
        self.assertEqual(progress.last_viewed_position, 120)
        self.assertTrue(progress.viewed)

    def test_video_file_upload(self):
        """Test that the uploaded video file exists"""
        self.assertTrue(os.path.exists(self.video.file.path))

    def tearDown(self):
        """Cleanup after tests"""
        if os.path.exists(self.video.file.path):
            os.remove(self.video.file.path)
        if os.path.exists(self.video.thumbnail.path):
            os.remove(self.video.thumbnail.path)