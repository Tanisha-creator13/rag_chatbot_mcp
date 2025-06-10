# import json
# from django.shortcuts import render

# # # Create your views here.
# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# from .mcp_server import MCPServer
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse 

# mcp = MCPServer()

# @csrf_exempt
# def rag_chat(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         query = data.get("query", "").strip().lower()
#     elif request.method == "GET":
#         query = request.GET.get("q", "").strip().lower()
#     else:
#         return JsonResponse({"error": "Method not allowed"}, status=405)

#     # Handle greetings or short messages
#     greetings = ["hello", "hi", "hey", "good morning", "good evening"]
#     if query in greetings or len(query) < 5:
#         return JsonResponse({"response": "Hello! How can I assist you today?"})

#     # Run similarity-based search
#     result, similarity = mcp.query_with_similarity(query)

#     # Handle irrelevant or unmatched queries
#     if similarity < 0.75:
#         return JsonResponse({
#             "response": "Sorry, I couldn’t find anything relevant to your question. Could you rephrase or ask something else?"
#         })

#     # Return valid response
#     return JsonResponse({"response": result})

from django.http import JsonResponse
# from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse
from .mcp_server import MCPServer
mcp = MCPServer()
@csrf_exempt
def rag_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("message", "").strip().lower()
        
        # Handle greetings and thanks directly
        greetings = ["hi", "hello", "hey","hiiiiiii","hellloooooo","heloooooo","heyyyy" "good morning", "good evening"]
        thanks = ["thanks", "thank you"]
        if query in greetings:
            return JsonResponse({"reply": "Hello! How can I assist you today?"})
        if query in thanks:
            return JsonResponse({"reply": "You're welcome! If you have any other questions, feel free to ask."})

        # Otherwise, use the RAG pipeline
        response = mcp.query(query)
        return JsonResponse({"reply": response})
    else:
        return JsonResponse({"reply": "Method not allowed"}, status=405)

