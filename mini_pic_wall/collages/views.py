from django.db.models import Subquery
from django.db.models.query import EmptyQuerySet
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import Serializer as EmptySerializer
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from users import permissions
from pictures.models import Picture
from pictures.serializers import HyperlinkedPictureSerializer
from . import serializers
from .models import Collage


class CollageViewSet(ModelViewSet):
    def get_object(self):
        if self.action == 'retrieve':
            assert 'owner' in self.get_serializer_class().Meta.fields
            collage = Collage.objects.select_related('owner').get(pk=self.kwargs['pk'])
            # self.check_object_permissions(self.request, collage)
            return collage
        else:
            collage = Collage.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, collage)
            return collage

    def get_queryset(self):
        match self.action:
            case 'list':
                return Collage.objects.all()
            case 'pictures' | 'detach':
                return Picture.objects.filter(collages=self.kwargs['pk'])
            case 'attach':
                collage = Collage.objects.filter(pk=self.kwargs['pk'])
                owner_of_collage = Subquery(collage.values('owner_id'))
                pictures_of_owner = Picture.objects.filter(owner=owner_of_collage)

                attached_pictures = (Collage.pictures.through.objects
                    .filter(collage_id=self.kwargs['pk']).values('picture_id'))

                not_attached_pictures_of_owner = (pictures_of_owner
                    .exclude(id__in=attached_pictures))

                return not_attached_pictures_of_owner
            case _:
                return EmptyQuerySet()

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.HyperlinkedCollageSerializer
            case 'retrieve':
                return serializers.CollageSerializer
            case 'pictures':
                return HyperlinkedPictureSerializer
            case 'attach':
                return serializers.AttachPictureOptionSerializer
            case 'detach':
                return serializers.DetachPictureOptionSerializer
            case _:
                return EmptySerializer

    def get_serializer(self, *args, **kwargs):
        if self.action in ['attach', 'detach']:
            kwargs['collage_pk'] = self.kwargs['pk']
        return super().get_serializer(*args, **kwargs)

    def get_permissions(self):
        permission_classes = [permissions.ReadOnly]
        if self.action == 'destroy':
            permission_classes = [permissions.IsObjectOwner]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def pictures(self, request, pk=None):
        return self.list(request)

    @action(detail=True, methods=['get'])
    def attach(self, request, pk=None):
        return self.list(request)

    @action(detail=True, methods=['get'])
    def detach(self, request, pk=None):
        return self.list(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attach(request, collage_pk, picture_pk, format=None):
    collage = Collage.objects.get(pk=collage_pk)
    if collage.owner_id != request.user.pk:
        raise PermissionDenied('You do not own this collage')

    picture = Picture.objects.get(pk=picture_pk)
    if picture.owner_id != request.user.pk:
        raise PermissionDenied('You do not own this picture')

    if collage.pictures.filter(pk=picture_pk).exists():
        return Response('Already attached')

    collage.pictures.add(picture)
    return Response('Successfully attached')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detach(request, collage_pk, picture_pk, format=None):
    collage = Collage.objects.get(pk=collage_pk)
    if collage.owner_id != request.user.pk:
        raise PermissionDenied('You do not own this collage')

    picture = Picture.objects.get(pk=picture_pk)
    if picture.owner_id != request.user.pk:
        raise PermissionDenied('You do not own this picture')

    if not collage.pictures.filter(pk=picture_pk).exists():
        return Response('Already detached')

    collage.pictures.remove(picture)
    return Response('Successfully detached')
