from rest_framework import viewsets, status
from rest_framework.serializers import Serializer as EmptySerializer
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.settings import api_settings
from django.contrib.auth import login, logout
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
        match self.action:
            case 'list':
                return serializers.HyperlinkedUserSerializer
            case 'retrieve' | 'create':
                return serializers.UserSerializer
            case 'deactivate':
                return serializers.UserPasswordSerializer
            case 'change':
                return serializers.UserUpdateSerializer
            case 'pictures':
                return {
                    'GET': serializers.HyperlinkedPictureSerializer,
                    'POST': serializers.PictureSerializer,
                }.get(self.request.method, EmptySerializer)
            case 'collages':
                return {
                    'GET': serializers.HyperlinkedCollageSerializer,
                    'POST': serializers.CollageSerializer,
                }.get(self.request.method, EmptySerializer)
            case _:
                return EmptySerializer

    def get_permissions(self):
        permission_classes = [permissions.ReadOnly]
        if self.action in ['deactivate', 'change', 'pictures', 'collages']:
            permission_classes = [permissions.IsUserThemselfOrReadOnly]
        elif self.action == 'create':
            permission_classes = []
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def deactivate(self, request, username=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user.is_active = False
        user.save()
        logout(request)
        return Response("Successfully deactivated")

    @action(detail=True, methods=['post'])
    def change(self, request, username=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = {'Location': reverse('user-detail', request=request, args=[user.username])}
        return Response(serializer.data, headers=headers)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self.action == 'create':
            user = serializer.save()
            login(self.request, user)

            url = reverse('user-detail', request=self.request, args=[user.username])
        else:
            instance = serializer.save(owner=self.get_object())

            if self.action == 'pictures':
                url = reverse('picture-detail', request=self.request, args=[instance.pk])
            elif self.action == 'collages':
                url = reverse('collage-detail', request=self.request, args=[instance.pk])

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers={'Location': url})


class PictureViewSet(viewsets.ModelViewSet):
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

    def get_permissions(self):
        permission_classes = [permissions.ReadOnly]
        if self.action == 'destroy':
            permission_classes = [permissions.IsPictureOwner]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def collages(self, request, pk=None):
        return self.list(request)

    @action(detail=True, methods=['get'])
    def attach(self, request, pk=None):
        data = []
        picture = self.get_object()
        collages = picture.owner.collages.exclude(pictures=picture).order_by('pk')
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

    def get_permissions(self):
        permission_classes = [permissions.ReadOnly]
        if self.action == 'destroy':
            permission_classes = [permissions.IsCollageOwner]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def pictures(self, request, pk=None):
        return self.list(request)

    @action(detail=True, methods=['get'])
    def attach(self, request, pk=None):
        data = []
        collage = self.get_object()
        pictures = collage.owner.pictures.exclude(collages=collage).order_by('pk')
        pictures = pictures if self.paginator is None else self.paginate_queryset(pictures)
        for picture in pictures:
            picture_url = reverse('picture-detail', request=request, args=[picture.pk])
            attach_url = reverse('collage-attach-picture', request=request, args=[collage.pk, picture.pk])
            data.append({'url': picture_url, 'name': picture.name, 'thumbnail': picture.image.thumbnail.url, 'attach': attach_url})
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
            data.append({'url': picture_url, 'name': picture.name, 'thumbnail': picture.image.thumbnail.url, 'detach': detach_url})
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


@api_view(['GET'])
def auth_list(request, format=None):
    return Response({
        'login': reverse('auth:login', request=request, format=format),
        'logout': reverse('auth:logout', request=request, format=format),
    })


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'auth': reverse('auth-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'picture': reverse('picture-list', request=request, format=format),
        'collage': reverse('collage-list', request=request, format=format),
    })
