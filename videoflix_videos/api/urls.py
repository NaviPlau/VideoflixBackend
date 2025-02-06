from django.urls import path
from .views import UploadVideoView

urlpatterns = [
    path('videos/upload/', UploadVideoView.as_view(), name='upload_video'),
]