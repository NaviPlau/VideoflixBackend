from django.urls import path
from .views import UploadVideoView, VideoListView

urlpatterns = [
    path('videos/upload/', UploadVideoView.as_view(), name='upload_video'),
    path('videos/', VideoListView.as_view(), name='video_list'),
]