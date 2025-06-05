from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .mcp_server import MCPServer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse 



mcp = MCPServer()

@csrf_exempt
def rag_chat(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        query = data.get("query", "Hello!")
    elif request.method == "GET":
        query = request.GET.get("q", "Hello!")
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    result = mcp.query(query)
    return JsonResponse({"response": result})
