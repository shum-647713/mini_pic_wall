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


class IsPictureOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_picture = models.Picture.objects.get(pk=view.kwargs['pk'])
        return request.user == accessed_picture.owner
