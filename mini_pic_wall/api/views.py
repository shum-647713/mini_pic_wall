from rest_framework import viewsets, status
from rest_framework.serializers import Serializer as EmptySerializer
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
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
            case 'create_collage':
                return serializers.CollageSerializer
            case _:
                return EmptySerializer

    def get_permissions(self):
        permission_classes = [permissions.ReadOnly]
        if self.action in ['upload_picture', 'create_collage']:
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

    @action(detail=True, methods=['post'])
    def create_collage(self, request, username=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(owner=user)
        headers = {'Location': reverse('collage-detail', request=request, args=[instance.pk])}
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

    @action(detail=True, methods=['get'])
    def attach(self, request, pk=None):
        data = []
        picture = self.get_object()
        collages = picture.owner.collages.all()
        for collage in collages:
            collage_url = reverse('collage-detail', request=request, args=[collage.pk])
            attach_url = reverse('picture-attach-collage', request=request, args=[picture.pk, collage.pk])
            data.append({'url': collage_url, 'name': collage.name, 'attach': attach_url})
        return Response(data)


class CollageViewSet(viewsets.ModelViewSet):
    queryset = models.Collage.objects.all()
    permission_classes = [permissions.ReadOnly]

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.HyperlinkedCollageSerializer
            case 'retrieve':
                return serializers.CollageSerializer
            case _:
                return EmptySerializer

    @action(detail=True, methods=['get'])
    def attach(self, request, pk=None):
        data = []
        collage = self.get_object()
        pictures = collage.owner.pictures.all()
        for picture in pictures:
            picture_url = reverse('picture-detail', request=request, args=[picture.pk])
            attach_url = reverse('collage-attach-picture', request=request, args=[collage.pk, picture.pk])
            data.append({'picture': picture_url, 'attach': attach_url})
        return Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsPictureAndCollageOwner])
def attach(request, picture_pk, collage_pk, format=None):
    collage = models.Collage.objects.get(pk=collage_pk)
    if collage.pictures.filter(pk=picture_pk).count() != 0:
        return Response("Already attached")
    picture = models.Picture.objects.get(pk=picture_pk)
    collage.pictures.add(picture)
    return Response("Successfully attached")
