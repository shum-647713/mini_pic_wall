from rest_framework import routers
from .views import PictureViewSet

router = routers.SimpleRouter()
router.register(r'pictures', PictureViewSet, basename='picture')

urlpatterns = router.urls
