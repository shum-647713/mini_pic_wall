from django.db.models import Subquery
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import Serializer as EmptySerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.reverse import reverse
import pictures.serializers
import collages.serializers
from pictures.models import Picture
from collages.models import Collage
from . import serializers, permissions


class UserViewSet(ModelViewSet):
    lookup_field = 'username'

    def get_object(self):
        if self.request.user.username == self.kwargs['username']:
            return self.request.user
        user = User.objects.get(username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user

    def get_queryset(self):
        match self.action:
            case 'pictures':
                user = User.objects.filter(username=self.kwargs['username'])
                return Picture.objects.filter(owner=Subquery(user.values('pk')))
            case 'collages':
                user = User.objects.filter(username=self.kwargs['username'])
                return Collage.objects.filter(owner=Subquery(user.values('pk')))
            case _:
                return User.objects.order_by('pk')

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.HyperlinkedUserSerializer
            case 'retrieve' | 'create':
                return serializers.UserSerializer
            case 'change':
                return serializers.UserUpdateSerializer
            case 'deactivate':
                return serializers.UserPasswordSerializer
            case 'pictures':
                return {
                    'GET': pictures.serializers.HyperlinkedPictureSerializer,
                    'POST': pictures.serializers.PictureSerializer,
                }.get(self.request.method, EmptySerializer)
            case 'collages':
                return {
                    'GET': collages.serializers.HyperlinkedCollageSerializer,
                    'POST': collages.serializers.CollageSerializer,
                }.get(self.request.method, EmptySerializer)
            case _:
                return EmptySerializer

    def get_permissions(self):
        match self.action:
            case 'change' | 'deactivate':
                permission_classes = [permissions.IsUserThemself]
            case 'pictures' | 'collages':
                permission_classes = [permissions.IsUserThemselfOrReadOnly]
            case 'create':
                permission_classes = []
            case _:
                permission_classes = [permissions.ReadOnly]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def change(self, request, username=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, username=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        user.is_active = False
        user.save()
        logout(request)
        return Response("Successfully deactivated")

    def list_or_create(self, request):
        return (self.list if request.method == 'GET' else self.create)(request)

    @action(detail=True, methods=['get', 'post'])
    def pictures(self, request, username=None):
        return self.list_or_create(request)

    @action(detail=True, methods=['get', 'post'])
    def collages(self, request, username=None):
        return self.list_or_create(request)

    def perform_create(self, serializer):
        if self.action == 'create':
            self.user = serializer.save()
            login(self.request, self.user)
        else:
            self.instance = serializer.save(owner=self.get_object())

    def reverse(self, *args, **kwargs):
        kwargs.setdefault('request', self.request)

        arg = kwargs.pop('arg', None)
        if arg is not None:
            kwargs.setdefault('args', [arg])

        return reverse(*args, **kwargs)

    def get_success_headers(self, data):
        match self.action:
            case 'create' | 'change':
                return {'Location': self.reverse('user-detail', arg=self.user.username)}
            case 'pictures':
                return {'Location': self.reverse('picture-detail', arg=self.instance.pk)}
            case 'collages':
                return {'Location': self.reverse('collage-detail', arg=self.instance.pk)}
            case _:
                return {}
