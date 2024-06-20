from celery import shared_task
from . import models


@shared_task(ignore_result=True)
def make_image_thumbnail(image_pk):
    image = models.Image.objects.get(pk=image_pk)
    image.make_thumbnail_now(save=True)
