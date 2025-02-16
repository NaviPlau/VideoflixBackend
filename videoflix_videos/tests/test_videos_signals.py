from django.test import TestCase
from unittest.mock import patch
from videoflix_videos.models import Video
from videoflix_videos.tasks import convert_to_hls
from django.core.files.uploadedfile import SimpleUploadedFile


class VideoSignalTestCase(TestCase):
    @patch("videoflix_videos.tasks.convert_to_hls.delay")
    def test_hls_conversion_signal(self, mock_convert_to_hls):
        """Test that the signal triggers HLS conversion when a video is created"""
        video_file = SimpleUploadedFile("test_video.mp4", b"dummy_video_data", content_type="video/mp4")
        thumbnail_file = SimpleUploadedFile("thumbnail.jpg", b"image_data", content_type="image/jpeg")

        video = Video.objects.create(
            title="Test Video",
            file=video_file,
            thumbnail=thumbnail_file,
            description="Test Description",
            genre="Action"
        )
        mock_convert_to_hls.assert_called_once_with(video.id)
