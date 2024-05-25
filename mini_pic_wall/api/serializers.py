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
    pictures = HyperlinkedPictureSerializer(many=True, read_only=True)
    collages = HyperlinkedCollageSerializer(many=True, read_only=True)
    upload_picture = serializers.HyperlinkedIdentityField(view_name='user-upload-picture', lookup_field='username')
    create_collage = serializers.HyperlinkedIdentityField(view_name='user-create-collage', lookup_field='username')

    class Meta:
        model = User
        fields = ['username', 'pictures', 'collages', 'upload_picture', 'create_collage']


class PictureSerializer(serializers.ModelSerializer):
    collages = HyperlinkedCollageSerializer(many=True, read_only=True)
    attach = serializers.HyperlinkedIdentityField(view_name='picture-attach')
    owner = HyperlinkedUserSerializer(read_only=True)

    class Meta:
        model = models.Picture
        fields = ['image', 'collages', 'attach', 'owner']


class CollageSerializer(serializers.ModelSerializer):
    pictures = HyperlinkedPictureSerializer(many=True, read_only=True)
    attach = serializers.HyperlinkedIdentityField(view_name='collage-attach')
    owner = HyperlinkedUserSerializer(read_only=True)

    class Meta:
        model = models.Collage
        fields = ['name', 'pictures', 'attach', 'owner']
