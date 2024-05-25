from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'pictures', views.PictureViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
