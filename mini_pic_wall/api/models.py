import os
import hashlib
from django.db import models
from django.core.files import storage


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


class Picture(models.Model):
    image = models.ImageField(upload_to='images/', storage=Sha256NameStorage())
    owner = models.ForeignKey('auth.User', related_name='pictures', on_delete=models.CASCADE)

    def __str__(self):
        return self.image.name


class Collage(models.Model):
    name = models.CharField(max_length=255)
    pictures = models.ManyToManyField(Picture, related_name='collages')
    owner = models.ForeignKey('auth.User', related_name='collages', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
