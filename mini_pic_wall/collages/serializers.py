from django.urls import reverse as django_reverse
from rest_framework import serializers
from rest_framework.reverse import reverse as drf_reverse
from optimized_serializers import HyperlinkedModelSerializer
from users.serializers import HyperlinkedUserSerializer
from pictures.serializers import HyperlinkedPictureSerializer
from . import models


class HyperlinkedCollageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Collage
        fields = ['url', 'name']
        load_only = ['pk', 'name']


class CollageSerializer(serializers.ModelSerializer):
    pictures = serializers.HyperlinkedIdentityField(view_name='collage-pictures')
    attach = serializers.HyperlinkedIdentityField(view_name='collage-attach')
    detach = serializers.HyperlinkedIdentityField(view_name='collage-detach')
    owner = HyperlinkedUserSerializer(read_only=True)

    class Meta:
        model = models.Collage
        fields = ['name', 'pictures', 'attach', 'detach', 'owner']


class PictureOptionSerializer(HyperlinkedPictureSerializer):
    def __init__(self, *args, **kwargs):
        self.collage_pk = kwargs.pop('collage_pk')
        super().__init__(*args, **kwargs)

    def reverse(self, *args, **kwargs):
        try:
            request = self._context['request']
            return drf_reverse(*args, **kwargs, request=request)
        except (AttributeError, KeyError):
            return django_reverse(*args, **kwargs)

class AttachPictureOptionSerializer(PictureOptionSerializer):
    attach = serializers.SerializerMethodField()

    class Meta(HyperlinkedPictureSerializer.Meta):
        model = models.Picture
        fields = HyperlinkedPictureSerializer.Meta.fields + ['attach']

    def get_attach(self, obj):
        return str(self.reverse('collage-attach-picture', kwargs={
            'collage_pk': self.collage_pk, 'picture_pk': obj.pk}))

class DetachPictureOptionSerializer(PictureOptionSerializer):
    detach = serializers.SerializerMethodField()

    class Meta(HyperlinkedPictureSerializer.Meta):
        model = models.Picture
        fields = HyperlinkedPictureSerializer.Meta.fields + ['detach']

    def get_detach(self, obj):
        return str(self.reverse('collage-detach-picture', kwargs={
            'collage_pk': self.collage_pk, 'picture_pk': obj.pk}))
