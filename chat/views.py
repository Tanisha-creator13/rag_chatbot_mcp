# from django.http import JsonResponse
# # from django.views.decorators.http import require_POST
# import json
# from django.views.decorators.csrf import csrf_exempt
# from django.http import StreamingHttpResponse
# from .mcp_server import MCPServer
# mcp = MCPServer()
# @csrf_exempt
# def rag_chat(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         query = data.get("message", "").strip().lower()
        
#         # Handle greetings
#         greetings = ["hi", "hello", "hey","hiiiiiii","hellloooooo","heloooooo","heyyyy" "good morning", "good evening"]
#         thanks = ["thanks", "thank you"]
#         if query in greetings:
#             return JsonResponse({"reply": "Hello! How can I assist you today?"})
#         if query in thanks:
#             return JsonResponse({"reply": "You're welcome! If you have any other questions, feel free to ask."})

#         # Otherwise, use the RAG pipeline
#         response = mcp.query(query)
#         return JsonResponse({"reply": response})
#     else:
#         return JsonResponse({"reply": "Method not allowed"}, status=405)

from .intent_classifier import IntentClassifier
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .mcp_server import MCPServer

from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

mcp = MCPServer()

intent_classifier = IntentClassifier()
predefined_responses = {
    "greeting": "Hello! How can I assist you today? 😊",
    "thanks": "You're most welcome! ",
    "goodbye": "Goodbye! Have a great day!",
    "other": "I'm here to help with information. Could you rephrase your question?",
}

@csrf_exempt
def rag_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("message", "").strip()
        
        intent = intent_classifier.classify(query)
        
        if intent in predefined_responses:
            return JsonResponse({"reply": predefined_responses[intent]})
        
        response = mcp.query(query)
        return JsonResponse({"reply": response})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
