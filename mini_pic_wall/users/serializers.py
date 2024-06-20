from string import ascii_letters, digits
from django.contrib.auth.models import User
from rest_framework import serializers
from optimized_serializers import HyperlinkedModelSerializer


class HyperlinkedUserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username']
        load_only = ['pk', 'username']
        extra_kwargs = {'url': {'lookup_field': 'username'}}


class UserSerializer(serializers.ModelSerializer):
    change = serializers.HyperlinkedIdentityField(view_name='user-change', lookup_field='username')
    deactivate = serializers.HyperlinkedIdentityField(view_name='user-deactivate', lookup_field='username')
    pictures = serializers.HyperlinkedIdentityField(view_name='user-pictures', lookup_field='username')
    collages = serializers.HyperlinkedIdentityField(view_name='user-collages', lookup_field='username')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'change', 'deactivate', 'pictures', 'collages']
        extra_kwargs = {
            'email': {'write_only': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.Serializer):
    username = serializers.ModelField(model_field=User.username.field)
    email = serializers.ModelField(model_field=User.email.field, write_only=True)
    password = serializers.ModelField(model_field=User.password.field, write_only=True)
    old_password = serializers.ModelField(model_field=User.password.field, write_only=True, required=True)

    def validate_username(self, value):
        allowed = set(ascii_letters + digits + '@.+-_')
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


class UserPasswordSerializer(serializers.Serializer):
    password = serializers.ModelField(model_field=User.password.field, write_only=True, required=True)

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('Incorrect password')
        return value
