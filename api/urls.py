from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import HabitTrackViewSet, HabitViewSet, TalkToGeminiView

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

habit_track_viewset = HabitTrackViewSet.as_view({
    'post': 'increment',
})

urlpatterns = [
    path('', include(router.urls)),
    path('habits/<int:pk>/increment/', habit_track_viewset, name='increment-habit'),
    path("talk-to-gemini/", TalkToGeminiView.as_view(), name="talk-to-gemini"),

]