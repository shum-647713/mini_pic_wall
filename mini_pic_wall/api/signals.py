from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from . import models


@receiver(post_delete, sender=models.Picture, dispatch_uid="delete_unreferenced_image")
def delete_unreferenced_image(sender, instance, **kwargs):
    if instance.image.pictures.count() == 0:
        instance.image.delete()

@receiver(pre_delete, sender=models.Image, dispatch_uid="check_image_thumbnail")
def check_image_thumbnail(sender, instance, **kwargs):
    if not instance.thumbnail:
        raise Exception("deleting an image whose thumbnail may be in the process of being created")

@receiver(post_delete, sender=models.Image, dispatch_uid="delete_image_files")
def delete_image_files(sender, instance, **kwargs):
    instance.uploaded_image.delete(save=False)
    instance.thumbnail.delete(save=False)
