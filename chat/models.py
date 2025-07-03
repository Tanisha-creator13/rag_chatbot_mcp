from django.db import models

# Create your models here.


# import uuid
import uuid
from uuid import uuid4
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()  # match Supabase
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, default="New Chat")

class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)     
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True) 