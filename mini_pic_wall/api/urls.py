from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'pictures', views.PictureViewSet, basename='picture')
router.register(r'collages', views.CollageViewSet, basename='collage')

urlpatterns = [
    path('', include(router.urls)),
    path('pictures/<picture_pk>/attach/<collage_pk>/', views.attach, name='picture-attach-collage'),
    path('pictures/<picture_pk>/detach/<collage_pk>/', views.detach, name='picture-detach-collage'),
    path('collages/<collage_pk>/attach/<picture_pk>/', views.attach, name='collage-attach-picture'),
    path('collages/<collage_pk>/detach/<picture_pk>/', views.detach, name='collage-detach-picture'),
    path('auth/', include('rest_framework.urls')),
]
