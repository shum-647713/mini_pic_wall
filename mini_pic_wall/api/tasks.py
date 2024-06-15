from celery import shared_task
from . import models


@shared_task(ignore_result=True)
def make_picture_thumbnail(picture_pk):
    picture = models.Picture.objects.get(pk=picture_pk)
    picture.make_thumbnail_now()
