from rest_framework import serializers
from django.contrib.auth.models import User
from . import models


class HyperlinkedUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username']
        extra_kwargs = {'url': {'lookup_field': 'username'}}


class HyperlinkedPictureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Picture
        fields = ['url', 'image']


class HyperlinkedCollageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Collage
        fields = ['url', 'name']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    pictures = serializers.HyperlinkedIdentityField(view_name='user-pictures', lookup_field='username')
    collages = serializers.HyperlinkedIdentityField(view_name='user-collages', lookup_field='username')

    class Meta:
        model = User
        fields = ['username', 'pictures', 'collages']


class PictureSerializer(serializers.ModelSerializer):
    collages = HyperlinkedCollageSerializer(many=True, read_only=True)
    attach = serializers.HyperlinkedIdentityField(view_name='picture-attach')
    detach = serializers.HyperlinkedIdentityField(view_name='picture-detach')
    owner = HyperlinkedUserSerializer(read_only=True)

    class Meta:
        model = models.Picture
        fields = ['image', 'collages', 'attach', 'detach', 'owner']


class CollageSerializer(serializers.ModelSerializer):
    pictures = HyperlinkedPictureSerializer(many=True, read_only=True)
    attach = serializers.HyperlinkedIdentityField(view_name='collage-attach')
    detach = serializers.HyperlinkedIdentityField(view_name='collage-detach')
    owner = HyperlinkedUserSerializer(read_only=True)

    class Meta:
        model = models.Collage
        fields = ['name', 'pictures', 'attach', 'detach', 'owner']
