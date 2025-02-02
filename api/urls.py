from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import GenerateMicrocourseView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path("generate-microcourse/", GenerateMicrocourseView.as_view(), name="talk-to-gemini"),
]