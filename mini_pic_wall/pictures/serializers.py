from django.db.models import F
from rest_framework import serializers
from users.serializers import HyperlinkedUserSerializer
from . import models


class HyperlinkedPictureSerializer(serializers.HyperlinkedModelSerializer):
    thumbnail = serializers.ImageField(source='image_thumbnail')

    class Meta:
        model = models.Picture
        fields = ['url', 'name', 'thumbnail']

    def __init__(self, *args, **kwargs):
        try: kwargs['data'] = kwargs['data'].select_related('image').values(
                'pk', 'name', image_thumbnail=F('image__thumbnail'))
        except: pass
        return super().__init__(*args, **kwargs)


class PictureSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='image.uploaded_image')
    thumbnail = serializers.ImageField(source='image.thumbnail', read_only=True)
    collages = serializers.HyperlinkedIdentityField(view_name='picture-collages')
    owner = HyperlinkedUserSerializer(read_only=True)

    class Meta:
        model = models.Picture
        fields = ['name', 'image', 'thumbnail', 'collages', 'owner']

    def create(self, validated_data):
        uploaded_image = validated_data.pop('image')['uploaded_image']
        image = models.Image.objects.create(uploaded_image=uploaded_image)
        return models.Picture.objects.create(image=image, **validated_data)
