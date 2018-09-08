from rest_framework import routers

from resources.views import CountryViewSet, AirportViewSet, AirlineViewSet

router = routers.DefaultRouter()
router.register("airlines", AirlineViewSet)
router.register("airports", AirportViewSet)
router.register("countries", CountryViewSet)

urlpatterns = router.urls
