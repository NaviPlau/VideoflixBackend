from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
from .tasks import convert_to_hls

@receiver(post_save, sender=Video)
def trigger_hls_conversion(sender, instance, created, **kwargs):
    if created:
        convert_to_hls.delay(instance.id)