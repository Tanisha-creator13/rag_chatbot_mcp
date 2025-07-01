from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, 
    rag_chat,
    ChatSessionListCreate,
    ChatMessageList,
    mcp_query
)

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    
    # Chat session endpoints
    path('sessions/', ChatSessionListCreate.as_view(), name='chat_sessions'),
    path('messages/<int:session_id>/', ChatMessageList.as_view(), name='chat_messages'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Main chat endpoint
    path('chat/', rag_chat, name='rag_chat'),

    path('mcp/query/', mcp_query, name='mcp_query'),
]
