import string
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
    deactivate = serializers.HyperlinkedIdentityField(view_name='user-deactivate', lookup_field='username')
    change = serializers.HyperlinkedIdentityField(view_name='user-change', lookup_field='username')
    pictures = serializers.HyperlinkedIdentityField(view_name='user-pictures', lookup_field='username')
    collages = serializers.HyperlinkedIdentityField(view_name='user-collages', lookup_field='username')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'deactivate', 'change', 'pictures', 'collages']
        extra_kwargs = {
            'email': {'write_only': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User(username = validated_data['username'], email = validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserPasswordSerializer(serializers.Serializer):
    password = serializers.ModelField(model_field=User()._meta.get_field('password'), write_only=True, required=True)

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('Incorrect password')
        return value


class UserUpdateSerializer(serializers.Serializer):
    username = serializers.ModelField(model_field=User()._meta.get_field('username'))
    email = serializers.ModelField(model_field=User()._meta.get_field('email'), write_only=True)
    password = serializers.ModelField(model_field=User()._meta.get_field('password'), write_only=True)
    old_password = serializers.ModelField(model_field=User()._meta.get_field('password'), write_only=True, required=True)

    def validate_username(self, value):
        allowed = set(string.ascii_letters + string.digits + '@.+-_')
        if not set(value) <= allowed:
            raise serializers.ValidationError('Invalid username. This value may contain only letters, numbers, and @/./+/-/_ characters.')
        return value

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('Incorrect old_password')
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if validated_data.get('password', False):
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


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
