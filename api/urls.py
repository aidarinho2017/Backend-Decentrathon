from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceViewSet, TimeSlotViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'resources', ResourceViewSet)
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
