from rest_framework import viewsets, status
from rest_framework.serializers import Serializer as EmptySerializer
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth.models import User
from . import serializers, permissions, models


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'

    def get_object(self):
        return User.objects.get(username=self.kwargs['username'])

    def get_queryset(self):
        match self.action:
            case 'pictures':
                return self.get_object().pictures.all().order_by('pk')
            case 'collages':
                return self.get_object().collages.all().order_by('pk')
            case _:
                return User.objects.all().order_by('pk')

    def get_serializer_class(self):
        match self.action, self.request.method:
            case 'list', _:
                return serializers.HyperlinkedUserSerializer
            case 'retrieve', _:
                return serializers.UserSerializer
            case 'pictures', 'GET':
                return serializers.HyperlinkedPictureSerializer
            case 'pictures', 'POST':
                return serializers.PictureSerializer
            case 'collages', 'GET':
                return serializers.HyperlinkedCollageSerializer
            case 'collages', 'POST':
                return serializers.CollageSerializer
            case _:
                return EmptySerializer

    def get_permissions(self):
        permission_classes = [permissions.ReadOnly]
        if self.action in ['pictures', 'collages']:
            permission_classes = [permissions.IsUserThemselfOrReadOnly]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get', 'post'])
    def pictures(self, request, username=None):
        if request.method == 'POST':
            return self.create(request)
        return self.list(request)

    @action(detail=True, methods=['get', 'post'])
    def collages(self, request, username=None):
        if request.method == 'POST':
            return self.create(request)
        return self.list(request)

    def perform_create(self, serializer):
        serializer.save(owner=self.get_object())


class PictureViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.ReadOnly]

    def get_object(self):
        return models.Picture.objects.get(pk=self.kwargs['pk'])

    def get_queryset(self):
        if self.action == 'collages':
            return self.get_object().collages.all().order_by('pk')
        return models.Picture.objects.all().order_by('pk')

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.HyperlinkedPictureSerializer
            case 'retrieve':
                return serializers.PictureSerializer
            case 'collages':
                return serializers.HyperlinkedCollageSerializer
            case _:
                return EmptySerializer

    @action(detail=True, methods=['get'])
    def collages(self, request, pk=None):
        return self.list(request)

    @action(detail=True, methods=['get'])
    def attach(self, request, pk=None):
        data = []
        picture = self.get_object()
        collages = picture.owner.collages.all().order_by('pk')
        collages = collages if self.paginator is None else self.paginate_queryset(collages)
        for collage in collages:
            collage_url = reverse('collage-detail', request=request, args=[collage.pk])
            attach_url = reverse('picture-attach-collage', request=request, args=[picture.pk, collage.pk])
            data.append({'url': collage_url, 'name': collage.name, 'attach': attach_url})
        return Response(data) if self.paginator is None else self.get_paginated_response(data)

    @action(detail=True, methods=['get'])
    def detach(self, request, pk=None):
        data = []
        picture = self.get_object()
        collages = picture.collages.all().order_by('pk')
        collages = collages if self.paginator is None else self.paginate_queryset(collages)
        for collage in collages:
            collage_url = reverse('collage-detail', request=request, args=[collage.pk])
            detach_url = reverse('picture-detach-collage', request=request, args=[picture.pk, collage.pk])
            data.append({'url': collage_url, 'name': collage.name, 'detach': detach_url})
        return Response(data) if self.paginator is None else self.get_paginated_response(data)


class CollageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.ReadOnly]

    def get_object(self):
        return models.Collage.objects.get(pk=self.kwargs['pk'])

    def get_queryset(self):
        if self.action == 'pictures':
            return self.get_object().pictures.all().order_by('pk')
        return models.Collage.objects.all().order_by('pk')

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.HyperlinkedCollageSerializer
            case 'retrieve':
                return serializers.CollageSerializer
            case 'pictures':
                return serializers.HyperlinkedPictureSerializer
            case _:
                return EmptySerializer

    @action(detail=True, methods=['get'])
    def pictures(self, request, pk=None):
        return self.list(request)

    @action(detail=True, methods=['get'])
    def attach(self, request, pk=None):
        data = []
        collage = self.get_object()
        pictures = collage.owner.pictures.all().order_by('pk')
        pictures = pictures if self.paginator is None else self.paginate_queryset(pictures)
        for picture in pictures:
            picture_url = reverse('picture-detail', request=request, args=[picture.pk])
            attach_url = reverse('collage-attach-picture', request=request, args=[collage.pk, picture.pk])
            data.append({'url': picture_url, 'attach': attach_url})
        return Response(data) if self.paginator is None else self.get_paginated_response(data)

    @action(detail=True, methods=['get'])
    def detach(self, request, pk=None):
        data = []
        collage = self.get_object()
        pictures = collage.pictures.all().order_by('pk')
        pictures = pictures if self.paginator is None else self.paginate_queryset(pictures)
        for picture in pictures:
            picture_url = reverse('picture-detail', request=request, args=[picture.pk])
            detach_url = reverse('collage-detach-picture', request=request, args=[collage.pk, picture.pk])
            data.append({'url': picture_url, 'detach': detach_url})
        return Response(data) if self.paginator is None else self.get_paginated_response(data)


@api_view(['POST'])
@permission_classes([permissions.IsPictureAndCollageOwner])
def attach(request, picture_pk, collage_pk, format=None):
    collage = models.Collage.objects.get(pk=collage_pk)
    if collage.pictures.filter(pk=picture_pk).count() != 0:
        return Response("Already attached")
    picture = models.Picture.objects.get(pk=picture_pk)
    collage.pictures.add(picture)
    return Response("Successfully attached")


@api_view(['POST'])
@permission_classes([permissions.IsPictureAndCollageOwner])
def detach(request, picture_pk, collage_pk, format=None):
    collage = models.Collage.objects.get(pk=collage_pk)
    if collage.pictures.filter(pk=picture_pk).count() == 0:
        return Response("Already detached")
    picture = models.Picture.objects.get(pk=picture_pk)
    collage.pictures.remove(picture)
    return Response("Successfully detached")
