from rest_framework import routers

from resources.views import AirportViewSet, AirlineViewSet

router = routers.DefaultRouter()
router.register("airlines", AirlineViewSet)
router.register("airports", AirportViewSet)

urlpatterns = router.urls
