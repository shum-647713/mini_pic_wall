from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'collages', views.CollageViewSet, basename='collage')

urlpatterns = [
    path('', include(router.urls)),
    path('collages/<collage_pk>/attach/<picture_pk>/', views.attach, name='collage-attach-picture'),
    path('collages/<collage_pk>/detach/<picture_pk>/', views.detach, name='collage-detach-picture'),
]
