# from uuid import uuid4, UUID
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view, permission_classes, authentication_classes
# from rest_framework.permissions import IsAuthenticated
# from chat.models import ChatSession, ChatMessage
# from chat.intent_classifier import IntentClassifier
# from chat.mcp_server import MCPServer
# from chat.tools.supabase_auth import SupabaseJWTAuthentication
# import json

# from rest_framework import generics
# from django.contrib.auth.models import User
# from .serializers import RegisterSerializer
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework import status

# from .models import ChatSession
# from .serializers import ChatSessionSerializer
# from .models import ChatMessage
# from .serializers import ChatMessageSerializer

# # Intent → Predefined
# intent_classifier = IntentClassifier()
# predefined_responses = {
#     "greeting": "Hello! How can I assist you today? 😊",
#     "thanks": "You're most welcome!",
#     "goodbye": "Goodbye! Have a great day!",
#     "other": "I'm here to help with information. Could you rephrase your question?",
# }

# # RAG LLM server
# mcp = MCPServer()

# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = RegisterSerializer
#     permission_classes = [AllowAny]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# class ChatSessionListCreate(generics.ListCreateAPIView):
#     serializer_class = ChatSessionSerializer
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [SupabaseJWTAuthentication]

#     def get_queryset(self):
#         return ChatSession.objects.filter(user_id=self.request.user.id)

#     def perform_create(self, serializer):
#         serializer.save(user_id=self.request.user.id)

# class ChatMessageList(generics.ListAPIView):
#     serializer_class = ChatMessageSerializer
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [SupabaseJWTAuthentication]

#     def get_queryset(self):
#         session_id = self.kwargs["session_id"]
#         return ChatMessage.objects.filter(
#             session_id=session_id,
#             session__user_id=self.request.user.id
#         )

# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([SupabaseJWTAuthentication])
# @permission_classes([IsAuthenticated])
# def rag_chat(request):
#     try:
#         data = json.loads(request.body)
#         query = data.get("message", "").strip()
#         session_id = data.get("session_id")

#         if not query:
#             return JsonResponse({"error": "Message is required."}, status=400)

#         # Get Supabase user UUID from JWT
#         user_id = UUID(request.user.payload["sub"])

#         # Ensure session exists or create
#         if session_id:
#             try:
#                 session = ChatSession.objects.get(id=session_id, user_id=user_id)
#             except ChatSession.DoesNotExist:
#                 session = ChatSession.objects.create(id=uuid4(), user_id=user_id, title=query[:50])
#         else:
#             session = ChatSession.objects.create(id=uuid4(), user_id=user_id, title=query[:50])

#         # Save user message
#         ChatMessage.objects.create(id=uuid4(), session=session, content=query, is_user=True)

#         # Classify intent
#         intent = intent_classifier.classify(query)

#         if intent in predefined_responses and intent != "other":
#             reply = predefined_responses[intent]
#         else:
#             reply = mcp.query(query) or "I'm sorry, I couldn't find relevant information."

#         # Save bot response
#         ChatMessage.objects.create(id=uuid4(), session=session, content=reply, is_user=False)

#         return JsonResponse({
#             "reply": reply,
#             "session_id": str(session.id)
#         })

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)


# from rest_framework_simplejwt.views import TokenObtainPairView
# from .serializers import CustomTokenObtainPairSerializer

# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer


from uuid import uuid4, UUID
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from chat.models import ChatSession, ChatMessage
from chat.intent_classifier import IntentClassifier
from chat.mcp_server import MCPServer
from chat.tools.supabase_auth import SupabaseJWTAuthentication
import json
import logging

from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import ChatSession
from .serializers import ChatSessionSerializer
from .models import ChatMessage
from .serializers import ChatMessageSerializer

from rest_framework.decorators import api_view
from django.http import JsonResponse
from chat.mcp_server import MCPServer

# Set up logging
logger = logging.getLogger(__name__)

# Intent → Predefined
intent_classifier = IntentClassifier()
predefined_responses = {
    "greeting": "Hello! How can I assist you today? 😊",
    "thanks": "You're most welcome!",
    "goodbye": "Goodbye! Have a great day!",
    "other": "I'm here to help with information. Could you rephrase your question?",
}

# RAG LLM server - Thread-safe singleton
mcp = MCPServer()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        session_id = self.kwargs["session_id"]
        return ChatMessage.objects.filter(
            session_id=session_id,
            session__user_id=self.request.user.id
        )


@api_view(['POST'])
def mcp_query(request):
    message = request.data.get('message', '')
    mcp = MCPServer()
    response = mcp.query(message)
    if isinstance(response, dict):
        return JsonResponse(response)
    return JsonResponse({"reply": response})



@csrf_exempt
@api_view(['POST'])
@authentication_classes([SupabaseJWTAuthentication])
@permission_classes([IsAuthenticated])
def rag_chat(request):
    try:
        data = json.loads(request.body)
        query = data.get("message", "").strip()
        session_id = data.get("session_id")

        if not query:
            return JsonResponse({"error": "Message is required."}, status=400)

        # Get Supabase user UUID from JWT
        try:
            user_id = UUID(request.user.payload["sub"])
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Invalid user payload: {str(e)}")
            return JsonResponse({"error": "Invalid user authentication"}, status=401)

        # Ensure session exists
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user_id=user_id)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create(id=uuid4(), user_id=user_id, title=query[:50])
        else:
            session = ChatSession.objects.create(id=uuid4(), user_id=user_id, title=query[:50])

        # Save user message
        ChatMessage.objects.create(id=uuid4(), session=session, content=query, is_user=True)

        # Classify intent
        intent = intent_classifier.classify(query)

        if intent in predefined_responses and intent != "other":
            reply = predefined_responses[intent]
            context_sources = []
        else:
            try:
                # Get MCP response 
                mcp_response = mcp.query(query)
                
                # Handle different response formats
                if isinstance(mcp_response, dict):
                    reply = mcp_response.get("response", "I couldn't find relevant information.")
                    context_sources = mcp_response.get("context", [])
                else:  # Backward compatibility
                    reply = mcp_response or "I'm sorry, I couldn't find relevant information."
                    context_sources = []
                
                
                if context_sources:
                    source_info = "\n\nSources: " + ", ".join([f"Doc {doc_id}" for doc_id in context_sources[:3]])
                    reply += source_info
                    
            except Exception as e:
                logger.error(f"MCP query error: {str(e)}")
                reply = "I'm having trouble accessing information right now. Please try again later."
                context_sources = []

        # Save bot response with context metadata
        ChatMessage.objects.create(
            id=uuid4(),
            session=session,
            content=reply,
            is_user=False,
            metadata={"context_sources": context_sources}  # Store context for analysis
        )

        return JsonResponse({
            "reply": reply,
            "session_id": str(session.id),
            "context": context_sources  # Return context to client
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        logger.exception("Unhandled error in rag_chat")
        return JsonResponse({"error": "Internal server error"}, status=500)


from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
