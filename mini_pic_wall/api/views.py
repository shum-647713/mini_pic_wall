from rest_framework import viewsets
from rest_framework.serializers import Serializer as EmptySerializer
from django.contrib.auth.models import User
from . import serializers, permissions

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = [permissions.ReadOnly]

    def get_serializer_class(self):
        match self.action:
            case 'list' | 'retrieve':
                return serializers.HyperlinkedUserSerializer
            case _:
                return EmptySerializer
