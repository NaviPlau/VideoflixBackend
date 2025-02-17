from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
from .tasks import convert_to_hls

@receiver(post_save, sender=Video)
def trigger_hls_conversion(sender, instance, created, **kwargs):
    """
    Signal receiver that triggers HLS conversion for a video when it is created.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Video): The actual instance being saved.
        created (bool): A boolean; True if a new record was created.
        **kwargs: Additional keyword arguments.
    """

    if created:
        convert_to_hls.delay(instance.id)