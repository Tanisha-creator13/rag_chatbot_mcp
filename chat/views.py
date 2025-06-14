from .intent_classifier import IntentClassifier
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .mcp_server import MCPServer

from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework.decorators import api_view, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication

mcp = MCPServer()

intent_classifier = IntentClassifier()
predefined_responses = {
    "greeting": "Hello! How can I assist you today? 😊",
    "thanks": "You're most welcome! ",
    "goodbye": "Goodbye! Have a great day!",
    "other": "I'm here to help with information. Could you rephrase your question?",
}

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from .models import ChatSession, ChatMessage 
from .serializers import ChatSessionSerializer, ChatMessageSerializer

class ChatSessionListCreate(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

class ChatMessageList(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return ChatMessage.objects.filter(
            session_id=session_id,
            session__user=self.request.user
        )

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rag_chat(request):
    try:
        data = json.loads(request.body)
        print("Request data:", data)
        print("Authenticated user:", request.user)

        query = data.get("message", "").strip()
        session_id = data.get("session_id")
        user = request.user

        if not session_id:
            return JsonResponse({"error": "session_id is required"}, status=400)

        try:
            session = ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create(user=user, title=query[:50])

        ChatMessage.objects.create(session=session, content=query, is_user=True)

        intent = intent_classifier.classify(query)
        reply = predefined_responses.get(intent, mcp.query(query))

        ChatMessage.objects.create(session=session, content=reply, is_user=False)

        return JsonResponse({
            "reply": reply,
            "session_id": str(session.id)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer