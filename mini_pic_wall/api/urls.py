from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'pictures', views.PictureViewSet)
router.register(r'collages', views.CollageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('pictures/<picture_pk>/attach/<collage_pk>/', views.attach, name='picture-attach-collage'),
    path('collages/<collage_pk>/attach/<picture_pk>/', views.attach, name='collage-attach-picture'),
    path('auth/', include('rest_framework.urls')),
]
