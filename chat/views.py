import json
from django.shortcuts import render

# # Create your views here.
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
from .mcp_server import MCPServer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse 

mcp = MCPServer()

@csrf_exempt
def rag_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("query", "").strip().lower()
    elif request.method == "GET":
        query = request.GET.get("q", "").strip().lower()
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Handle greetings or short messages
    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    if query in greetings or len(query) < 5:
        return JsonResponse({"response": "Hello! How can I assist you today?"})

    # Run similarity-based search
    result, similarity = mcp.query_with_similarity(query)

    # Handle irrelevant or unmatched queries
    if similarity < 0.75:
        return JsonResponse({
            "response": "Sorry, I couldn’t find anything relevant to your question. Could you rephrase or ask something else?"
        })

    # Return valid response
    return JsonResponse({"response": result})
