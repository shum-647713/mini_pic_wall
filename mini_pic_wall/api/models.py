import os
import hashlib
from django.db import models


def hash_image_upload(instance, filename):
    name, ext = os.path.splitext(filename)
    ctx = hashlib.sha256()
    if instance.image.multiple_chunks():
        for data in instance.image.chunks(4096):
            ctx.update(data)
    else:
        ctx.update(instance.image.read())
    return os.path.join('images/', ctx.hexdigest() + ext)

class Picture(models.Model):
    image = models.ImageField(upload_to=hash_image_upload, max_length=255)
    owner = models.ForeignKey('auth.User', related_name='pictures', on_delete=models.CASCADE)

    def __str__(self):
        return self.image.name


class Collage(models.Model):
    name = models.CharField(max_length=255)
    pictures = models.ManyToManyField(Picture, related_name='collages')
    owner = models.ForeignKey('auth.User', related_name='collages', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
