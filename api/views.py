import requests
from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

import traceback
import google.generativeai as genai

from .models import Habit, HabitTrack
from .serializers import UserSerializer, HabitSerializer, HabitTrackSerializer

# Directly set the API key (Not recommended)
genai.configure(api_key='AIzaSyAsrJnW0dNtK0LmI-FlggNbr8LG14C5EFg')

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

            # Configure generation parameters
            generation_config = {
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }

            # Create the model
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
            )

            # Start a chat session
            chat_session = model.start_chat(history=[])

            # Send the user's message to the model
            response = chat_session.send_message(user_message)

            # Extract the generated text
            generated_text = response.text

            return Response({"reply": generated_text}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for debugging
            print("Exception occurred:", traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#