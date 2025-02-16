from django.test import TestCase
from unittest.mock import patch, MagicMock
from videoflix_videos.models import Video
from videoflix_videos.tasks import convert_to_hls, test_celery_task
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class CeleryTasksTestCase(TestCase):
    def setUp(self):
        """Set up test data for Celery tasks"""
        self.video_file = SimpleUploadedFile("test_video.mp4", b"dummy_video_data", content_type="video/mp4")
        self.video = Video.objects.create(
            title="Test Video",
            file=self.video_file,
            description="This is a test video",
            genre="Action"
        )

    @patch("videoflix_videos.tasks.subprocess.run")
    @patch("os.makedirs") 
    @patch("builtins.open", new_callable=MagicMock) 
    @patch("videoflix_videos.tasks.logger")  
    def test_convert_to_hls(self, mock_logger, mock_open, mock_makedirs, mock_subprocess):
        """Test HLS conversion task with all dependencies mocked"""
        mock_subprocess.return_value = MagicMock()
        convert_to_hls(self.video.id)
        mock_makedirs.assert_called_once()
        self.assertEqual(mock_subprocess.call_count, 4)
        mock_open.assert_called_once_with(
            os.path.join('media', 'videos', 'hls', str(self.video.id), 'master.m3u8'), 'w'
        )

        mock_logger.info.assert_any_call(f"Starting HLS conversion for video ID: {self.video.id}")
        mock_logger.info.assert_any_call(f"Successfully completed HLS conversion for video ID: {self.video.id}")
        self.video.refresh_from_db()
        self.assertIsNotNone(self.video.hls_master_playlist)

    def test_test_celery_task(self):
        """Test a simple Celery task"""
        result = test_celery_task()
        self.assertEqual(result, "Task completed")

    def tearDown(self):
        """Cleanup after tests"""
        if os.path.exists(self.video.file.path):
            os.remove(self.video.file.path)
