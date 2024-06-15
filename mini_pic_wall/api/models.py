import os
import hashlib
from django.db import models, transaction
from django.core.files import storage
from .tasks import make_picture_thumbnail
from PIL import Image
from io import BytesIO
from django.core.files import File


class Sha256NameStorage(storage.FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise(Exception("name's length is greater than max_length"))
        return name

    @staticmethod
    def get_sha256_hash(content):
        content.seek(0)
        sha256 = hashlib.sha256()
        for chunk in content.chunks():
            sha256.update(chunk)
        content.seek(0)
        return sha256.hexdigest()

    def _save(self, name, content):
        _name, ext = os.path.splitext(name)
        dirname = os.path.dirname(name)
        sha256_hash = self.get_sha256_hash(content)
        new_name = os.path.join(dirname, sha256_hash + ext)
        if self.exists(new_name):
            return new_name
        return super()._save(new_name, content)


class PictureManager(models.Manager):
    def create(self, *, make_thumbnail=True, **kwargs):
        picture = super().create(**kwargs)
        if make_thumbnail and 'thumbnail' not in kwargs:
            picture.make_thumbnail_on_commit()
        return picture

class Picture(models.Model):
    image = models.ImageField(upload_to='images/', storage=Sha256NameStorage())
    thumbnail = models.ImageField(upload_to='thumbnails/', storage=Sha256NameStorage(), blank=True)
    owner = models.ForeignKey('auth.User', related_name='pictures', on_delete=models.CASCADE)

    objects = PictureManager()

    def make_thumbnail_on_commit(self):
        transaction.on_commit(self.make_thumbnail_async)

    def make_thumbnail_async(self):
        make_picture_thumbnail.apply_async(args=(self.pk,), ignore_result=True)

    def make_thumbnail_now(self):
        if self.thumbnail: return

        with Image.open(self.image.path) as image:
            image.thumbnail(size=(128, 128))
            thumbnail_bytes = BytesIO()
            image.save(thumbnail_bytes, format='png')
            thumbnail_file = File(thumbnail_bytes, name='thumbnail.png')
            self.thumbnail.save(name='thumbnail.png', content=thumbnail_file, save=True)

    def __str__(self):
        return self.image.name


class Collage(models.Model):
    name = models.CharField(max_length=255)
    pictures = models.ManyToManyField(Picture, related_name='collages')
    owner = models.ForeignKey('auth.User', related_name='collages', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
