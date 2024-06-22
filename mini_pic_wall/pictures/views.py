from django.db.models.query import EmptyQuerySet
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import Serializer as EmptySerializer
from rest_framework.decorators import action
from users import permissions
from collages.models import Collage
from collages.serializers import HyperlinkedCollageSerializer
from . import serializers
from .models import Picture


class PictureViewSet(ModelViewSet):
    def get_object(self):
        if self.action == 'retrieve':
            assert 'thumbnail' in self.get_serializer_class().Meta.fields
            assert 'owner' in self.get_serializer_class().Meta.fields
            picture = Picture.objects.select_related('image', 'owner').get(pk=self.kwargs['pk'])
            # self.check_object_permissions(self.request, picture)
            return picture
        else:
            picture = Picture.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, picture)
            return picture

    def get_queryset(self):
        match self.action:
            case 'list':
                return Picture.objects.all()
            case 'collages':
                return Collage.objects.filter(pictures=self.kwargs['pk'])
            case _:
                return EmptyQuerySet()

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.HyperlinkedPictureSerializer
            case 'retrieve':
                return serializers.PictureSerializer
            case 'collages':
                return HyperlinkedCollageSerializer
            case _:
                return EmptySerializer

    def get_permissions(self):
        permission_classes = [permissions.ReadOnly]
        if self.action == 'destroy':
            permission_classes = [permissions.IsObjectOwner]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def collages(self, request, pk=None):
        return self.list(request)
