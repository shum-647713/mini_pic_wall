from rest_framework import viewsets, status
from rest_framework.serializers import Serializer as EmptySerializer
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from . import serializers, permissions, models


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.HyperlinkedUserSerializer
            case 'retrieve':
                return serializers.UserSerializer
            case 'upload_picture':
                return serializers.PictureSerializer
            case _:
                return EmptySerializer

    def get_permissions(self):
        permission_classes = [permissions.ReadOnly]
        if self.action == 'upload_picture':
            permission_classes = [permissions.IsUserThemself]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def upload_picture(self, request, username=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(owner=user)
        headers = {'Location': reverse('picture-detail', request=request, args=[instance.pk])}
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PictureViewSet(viewsets.ModelViewSet):
    queryset = models.Picture.objects.all()
    permission_classes = [permissions.ReadOnly]

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.HyperlinkedPictureSerializer
            case 'retrieve':
                return serializers.PictureSerializer
            case _:
                return EmptySerializer
