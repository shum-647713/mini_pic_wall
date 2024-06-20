from rest_framework import serializers
from optimized_serializers import HyperlinkedModelSerializer
from users.serializers import HyperlinkedUserSerializer
from . import models


class HyperlinkedPictureSerializer(HyperlinkedModelSerializer):
    thumbnail = serializers.ImageField(source='image.thumbnail')

    class Meta:
        model = models.Picture
        fields = ['url', 'name', 'thumbnail']
        select_related = ['image']
        load_only = ['pk', 'name', 'image__thumbnail']


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
