from rest_framework import permissions
from django.contrib.auth.models import User
from . import models


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsUserThemself(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_user = User.objects.get(username=view.kwargs['username'])
        return request.user == accessed_user


class IsUserThemselfOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_user = User.objects.get(username=view.kwargs['username'])
        safe_method = request.method in permissions.SAFE_METHODS
        return (request.user == accessed_user) or safe_method


class IsPictureOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_picture = models.Picture.objects.get(pk=view.kwargs['pk'])
        return request.user == accessed_picture.owner


class IsPictureOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_picture = models.Picture.objects.get(pk=view.kwargs['pk'])
        safe_method = request.method in permissions.SAFE_METHODS
        return (request.user == accessed_picture.owner) or safe_method


class IsCollageOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_collage = models.Collage.objects.get(pk=view.kwargs['pk'])
        return request.user == accessed_collage.owner


class IsCollageOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_collage = models.Collage.objects.get(pk=view.kwargs['pk'])
        safe_method = request.method in permissions.SAFE_METHODS
        return (request.user == accessed_collage.owner) or safe_method


class IsPictureAndCollageOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_picture = models.Picture.objects.get(pk=view.kwargs['picture_pk'])
        accessed_collage = models.Collage.objects.get(pk=view.kwargs['collage_pk'])
        return (request.user == accessed_picture.owner) and (request.user == accessed_collage.owner)


class IsPictureAndCollageOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_picture = models.Picture.objects.get(pk=view.kwargs['picture_pk'])
        accessed_collage = models.Collage.objects.get(pk=view.kwargs['collage_pk'])
        is_owner = (request.user == accessed_picture.owner) and (request.user == accessed_collage.owner)
        return is_owner or (request.method in permissions.SAFE_METHODS)
