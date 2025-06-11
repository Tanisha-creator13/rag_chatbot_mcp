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


from .models import ChatSession, ChatMessage  # Changed from Conversation
from .serializers import ChatSessionSerializer, ChatMessageSerializer  # New serializers

# Remove Conversation-related views and keep only session-based views
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
@permission_classes([IsAuthenticated])
def rag_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("message", "").strip()
            session_id = data.get("session_id")  # Changed from conversation_id
            user = request.user

            # Get or create session
            if session_id:
                session = ChatSession.objects.get(id=session_id, user=user)
            else:
                session = ChatSession.objects.create(user=user, title=query[:50])

            # Save user message
            ChatMessage.objects.create(
                session=session,
                content=query,
                is_user=True
            )

            # Intent handling remains same
            intent = intent_classifier.classify(query)
            reply = predefined_responses[intent] if intent in predefined_responses else mcp.query(query)

            # Save bot response
            ChatMessage.objects.create(
                session=session,
                content=reply,
                is_user=False
            )

            return JsonResponse({
                "reply": reply,
                "session_id": str(session.id)  # Changed key
            })

        except Exception as e:
            print(f"Chat error: {str(e)}")
            return JsonResponse({"error": "Internal server error"}, status=500)
