from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from videoflix_videos.models import Video, UserVideoProgress
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class VideoAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data for API views"""
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.video_file = SimpleUploadedFile("test_video.mp4", b"dummy_video_data", content_type="video/mp4")
        self.thumbnail_file = SimpleUploadedFile("thumbnail.jpg", b"image_data", content_type="image/jpeg")
        self.video = Video.objects.create(
            title="Test Video",
            file=self.video_file,
            thumbnail=self.thumbnail_file,
            description="Test Description",
            genre="Action"
        )

        self.progress = UserVideoProgress.objects.create(
            user=self.user,
            video=self.video,
            last_viewed_position=30,
            viewed=True
        )

    def test_upload_video_as_admin(self):
        """Test uploading a new video as an admin"""
        admin_user = User.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.force_authenticate(user=admin_user)

        url = "/videoflix/api/videos/upload/"
        data = {
            "title": "New Test Video",
            "file": SimpleUploadedFile("new_test.mp4", b"video_data", content_type="video/mp4"),
            "thumbnail": SimpleUploadedFile("thumbnail.jpg", b"image_data", content_type="image/jpeg"),
            "description": "New Description",
            "genre": "Drama"
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("video_id", response.data)

    def test_list_videos_authenticated(self):
        """Test retrieving a list of videos (authenticated user)"""
        url = "/videoflix/api/videos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_list_videos_unauthenticated(self):
        """Test retrieving a list of videos fails when unauthenticated"""
        self.client.logout()
        url = "/videoflix/api/videos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_single_video(self):
        """Test retrieving a single video"""
        url = f"/videoflix/api/videos/{self.video.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.video.title)

    def test_video_progress_update(self):
        """Test updating video progress"""
        url = f"/videoflix/api/video/{self.video.id}/progress/"
        data = {
            "last_viewed_position": 120,
            "viewed": True
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["last_viewed_position"], 120)

    def test_video_progress_update_unauthenticated(self):
        """Test updating video progress fails for unauthenticated user"""
        self.client.logout()
        url = f"/videoflix/api/video/{self.video.id}/progress/"
        data = {
            "last_viewed_position": 120,
            "viewed": True
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_upload_video_invalid(self):
        """Test uploading a video with missing fields (should fail, even for admin users)"""
        admin_user = User.objects.create_superuser(username='adminuser2', password='adminpassword2')
        self.client.force_authenticate(user=admin_user) 

        url = "/videoflix/api/videos/upload/"
        data = {
            "title": "Invalid Video",
        }
        response = self.client.post(url, data, format="multipart")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
        self.assertIn("file", response.data)


    
    
    
    def tearDown(self):
        """Cleanup created files"""
        for file in [self.video.file, self.video.thumbnail]:
            if file and hasattr(file, 'path') and os.path.exists(file.path):
                os.remove(file.path)
