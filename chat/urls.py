from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, 
    rag_chat,
    ChatSessionListCreate,
    ChatMessageList
)

urlpatterns = [
    # Auth endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    
    # Chat session endpoints
    path('api/sessions/', ChatSessionListCreate.as_view(), name='chat_sessions'),
    path('api/messages/<int:session_id>/', ChatMessageList.as_view(), name='chat_messages'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Main chat endpoint
    path('api/chat/', rag_chat, name='rag_chat'),
]
