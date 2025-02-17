from django.apps import AppConfig


class VideoflixVideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videoflix_videos'

    def ready(self):
        """
        This method is called when the Django application is ready.

        It imports the signals module from the videoflix_videos package. This is
        typically done to ensure that signal handlers are connected when the app
        is initialized.
        """

        import videoflix_videos.signals