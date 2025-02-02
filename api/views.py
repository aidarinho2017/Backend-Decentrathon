import random
from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

import traceback
import google.generativeai as genai

from .models import Microcourse, QuizQuestion, UserScore
from .serializers import UserSerializer

# Directly set the API key (Not recommended)
genai.configure(api_key='AIzaSyAEqtfxDLSE6fgwp7pmDNbv8pSdYSJ92og')

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class GenerateMicrocourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            topics = ["Machine Learning Basics", "Neural Networks", "AI Ethics", "Computer Vision",
                      "Reinforcement Learning"]
            selected_topic = random.choice(topics)

            generation_config = {
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
            )

            prompt_course = f"Generate an engaging microcourse on {selected_topic}, It must be like a story, very interesting for readers"
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt_course)
            course_content = response.text

            microcourse = Microcourse.objects.create(title=selected_topic, content=course_content)

            prompt_quiz = f"Generate one high-quality multiple-choice question with four options based on the following content:\n{course_content}\nFormat: Question, Option A, Option B, Option C, Option D, Correct Option (A/B/C/D)."
            response = chat_session.send_message(prompt_quiz)
            quiz_text = response.text.split('\n')

            if len(quiz_text) >= 6:
                question = QuizQuestion.objects.create(
                    microcourse=microcourse,
                    question_text=quiz_text[0],
                    option_a=quiz_text[1],
                    option_b=quiz_text[2],
                    option_c=quiz_text[3],
                    option_d=quiz_text[4],
                    correct_option=quiz_text[5].strip()
                )

            return Response({
                "title": microcourse.title,
                "content": microcourse.content,
                "quiz": {
                    "question_text": question.question_text,
                    "options": [question.option_a, question.option_b, question.option_c, question.option_d],
                    "correct_option": question.correct_option
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception occurred:", traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# View to Increment User Score
class IncrementUserScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user_score, created = UserScore.objects.get_or_create(user=user)
            user_score.score += 10  # Increment score by 10 points
            user_score.save()
            return Response({"message": "Score updated successfully", "new_score": user_score.score},
                            status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception occurred:", traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)