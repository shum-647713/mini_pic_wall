from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def root(request, format=None):
    return Response({
        'api': reverse('api-root', request=request, format=format),
        'auth': reverse('auth-root', request=request, format=format),
    })


@api_view(['GET'])
def auth_root(request, format=None):
    return Response({
        'login': reverse('auth:login', request=request, format=format),
        'logout': reverse('auth:logout', request=request, format=format),
    })


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'pictures': reverse('picture-list', request=request, format=format),
        'collages': reverse('collage-list', request=request, format=format),
    })
