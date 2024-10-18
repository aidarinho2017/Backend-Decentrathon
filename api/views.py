import requests
from django.contrib.auth.models import User
from requests import Response
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView

from .models import Habit, HabitTrack
from .serializers import UserSerializer, HabitSerializer, HabitTrackSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
import google.generativeai as genai
import os


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitTrackViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def increment(self, request, pk=None):
        try:
            habit = Habit.objects.get(pk=pk, user=request.user)
            track, created = HabitTrack.objects.get_or_create(habit=habit)
            track.increment()
            return Response(HabitTrackSerializer(track).data, status=status.HTTP_200_OK)
        except Habit.DoesNotExist:
            return Response({'error': 'Habit not found'}, status=status.HTTP_404_NOT_FOUND)


genai.configure(api_key=os.getenv("AIzaSyDYbBqbpukIamZIVBVa9i5yUoO4atK1Mj8"))


class TalkToGeminiView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    def post(self, request):
        try:
            # Extract message from the request body
            user_message = request.data.get("message", "")
            if not user_message:
                return Response(
                    {"error": "Message is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare the request to Gemini API
            gemini_url = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-1.5-flash:generateText"
            api_key = os.getenv("AIzaSyDYbBqbpukIamZIVBVa9i5yUoO4atK1Mj8")  # Load API key from environment

            headers = {"Content-Type": "application/json"}
            payload = {
                "prompt": {"text": user_message},
                "temperature": 0.7  # Control creativity (0.0 - 1.0)
            }

            # Send request to Gemini API
            response = requests.post(
                f"{gemini_url}?key={api_key}",
                json=payload,
                headers=headers
            )

            # Handle the response from Gemini
            if response.status_code == 200:
                generated_text = response.json().get("candidates", [{}])[0].get("output", "")
                return Response({"reply": generated_text}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to generate content"},
                    status=response.status_code
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)