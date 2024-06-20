from django.db import models
from django.conf import settings
from pictures.models import Picture


class Collage(models.Model):
    name = models.CharField(max_length=255)
    pictures = models.ManyToManyField(Picture)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        default_related_name = '%(model_name)ss'
        ordering = ['pk']

    def __str__(self):
        return self.name
