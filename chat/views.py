from uuid import uuid4
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

from rest_framework.decorators import api_view
from chat.tools.supabase_auth import SupabaseJWTAuthentication 
from rest_framework.decorators import authentication_classes
from uuid import UUID


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
    authentication_classes = [SupabaseJWTAuthentication]

    def get_queryset(self):
        return ChatSession.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

class ChatMessageList(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SupabaseJWTAuthentication]

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return ChatMessage.objects.filter(
            session_id=session_id,
            session__user_id=self.request.user.id
        )

@csrf_exempt
@api_view(['POST'])
@authentication_classes([SupabaseJWTAuthentication])
@permission_classes([IsAuthenticated])
def rag_chat(request):
    try:
        data = json.loads(request.body)
        query = data.get("message", "").strip()
        session_id = data.get("session_id")
        user_id = UUID(request.user.payload["sub"])  # Supabase user ID from JWT

        if not session_id:
            return JsonResponse({"error": "session_id is required"}, status=400)

        try:
            session = ChatSession.objects.get(id=session_id, user_id=user_id)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create(id=uuid4(), user_id=user_id, title=query[:50])

        ChatMessage.objects.create(id=uuid4(), session=session, content=query, is_user=True)

        intent = intent_classifier.classify(query)
        if intent in predefined_responses and intent != "other":
            reply = predefined_responses[intent]
        else:
            print(f"Calling RAG MCP with query: {query}")
            reply = mcp.query(query)  


        ChatMessage.objects.create(id=uuid4(), session=session, content=reply, is_user=False)

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
