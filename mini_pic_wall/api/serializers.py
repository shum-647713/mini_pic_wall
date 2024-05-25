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


class UserSerializer(serializers.HyperlinkedModelSerializer):
    pictures = HyperlinkedPictureSerializer(many=True, read_only=True)
    upload_picture = serializers.HyperlinkedIdentityField(view_name='user-upload-picture', lookup_field='username')

    class Meta:
        model = User
        fields = ['username', 'pictures', 'upload_picture']


class PictureSerializer(serializers.ModelSerializer):
    owner = HyperlinkedUserSerializer(read_only=True)

    class Meta:
        model = models.Picture
        fields = ['image', 'owner']
