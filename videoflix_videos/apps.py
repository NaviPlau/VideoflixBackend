from django.apps import AppConfig


class VideoflixVideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videoflix_videos'

    def ready(self):
        import videoflix_videos.signals