import os
import io
import hashlib
from time import strftime
import PIL
from django.db import models, transaction
from django.conf import settings
from django.core.files import File
from .tasks import make_image_thumbnail


class ImageManager(models.Manager):
    def create(self, uploaded_image):
        sha256 = hashlib.sha256()
        for chunk in uploaded_image.chunks():
            sha256.update(chunk)

        _name, ext = os.path.splitext(uploaded_image.name)
        sha256_name = sha256.hexdigest() + ext

        upload_to = self.model.uploaded_image.field.upload_to
        if not callable(upload_to):
            filename = os.path.join(strftime(upload_to), sha256_name)
            same_image = self.filter(uploaded_image=filename).first()
            if same_image: return same_image

        uploaded_image.name = sha256_name
        new_image = super().create(uploaded_image=uploaded_image)
        new_image.make_thumbnail_on_commit()
        return new_image

class Image(models.Model):
    uploaded_image = models.ImageField(upload_to='images/', unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)
    thumbnail_size = (128, 128)
    thumbnail_format = 'png'

    objects = ImageManager()

    class Meta:
        ordering = ['pk']

    def make_thumbnail_on_commit(self):
        transaction.on_commit(self.make_thumbnail_async)

    def make_thumbnail_async(self):
        make_image_thumbnail.apply_async(args=(self.pk,), ignore_result=True)

    def make_thumbnail_now(self, save=True):
        if self.thumbnail: return

        with PIL.Image.open(self.uploaded_image.path) as image:
            image.thumbnail(size=self.thumbnail_size)

            thumbnail_bytes = io.BytesIO()
            image.save(thumbnail_bytes, format=self.thumbnail_format)

            thumbnail_bytes.seek(0)
            sha256_hash = hashlib.sha256(thumbnail_bytes.read()).hexdigest()
            sha256_name = sha256_hash + '.' + self.thumbnail_format

            thumbnail_bytes.seek(0)
            thumbnail_file = File(thumbnail_bytes, name=sha256_name)
            self.thumbnail.save(name=sha256_name, content=thumbnail_file, save=save)

    def __str__(self):
        return os.path.basename(self.uploaded_image.name)


class Picture(models.Model):
    name = models.CharField(max_length=255)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        default_related_name = '%(model_name)ss'
        ordering = ['pk']

    def __str__(self):
        return self.name
